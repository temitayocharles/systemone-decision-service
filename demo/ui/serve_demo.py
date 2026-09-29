#!/usr/bin/env python3
"""Serve the System One workspace, proxy APIs, and expose a read-only local source.

The browser uses one origin:
- /health and /v2/* -> System One runtime
- /rag/*            -> RAG service, with /rag removed
- /local/downloads/* -> read-only Downloads adapter on the host Mac
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Dict, List

HERE = Path(__file__).resolve().parent
UI_FILE = HERE / "system-one-demo-ui.html"
TEXT_EXTENSIONS = {
    ".txt", ".md", ".markdown", ".csv", ".json", ".yaml", ".yml",
    ".log", ".xml", ".html", ".htm", ".py", ".js", ".ts", ".tsx",
    ".jsx", ".css", ".sh", ".zsh", ".bash", ".ini", ".cfg", ".toml",
}
MAX_FILES = 250
MAX_TEXT_BYTES = 512 * 1024


def _iso_timestamp(epoch: float) -> str:
    return datetime.fromtimestamp(epoch, tz=timezone.utc).isoformat()


def scan_local_root(root: Path) -> List[Dict]:
    if not root.exists() or not root.is_dir():
        raise FileNotFoundError(f"Local source directory not found: {root}")

    files: List[Dict] = []
    for path in sorted(root.iterdir(), key=lambda p: p.name.lower()):
        if len(files) >= MAX_FILES:
            break
        if not path.is_file() or path.name.startswith("."):
            continue

        stat = path.stat()
        suffix = path.suffix.lower()
        mimetype = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        text = ""
        content_mode = "metadata"

        if suffix in TEXT_EXTENSIONS and stat.st_size <= MAX_TEXT_BYTES:
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
                content_mode = "text"
            except OSError:
                text = ""

        metadata_text = (
            f"File: {path.name}\n"
            f"Type: {mimetype}\n"
            f"Extension: {suffix or '(none)'}\n"
            f"Size bytes: {stat.st_size}\n"
            f"Modified: {_iso_timestamp(stat.st_mtime)}\n"
        )
        content = metadata_text
        if text:
            content += f"\nExtracted text:\n{text}"

        files.append({
            "title": path.name,
            "content": content,
            "metadata": {
                "source": path.name,
                "source_path": str(path),
                "source_type": "local_file",
                "collection": "downloads",
                "extension": suffix,
                "mimetype": mimetype,
                "size_bytes": stat.st_size,
                "modified_at": _iso_timestamp(stat.st_mtime),
                "content_mode": content_mode,
            },
        })
    return files


class Handler(BaseHTTPRequestHandler):
    runtime = "http://localhost:8002"
    rag = "http://localhost:8001"
    local_root = Path.home() / "Downloads"

    def log_message(self, *args):
        pass

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _json(self, status: int, payload: Dict):
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self._cors()
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def _serve_ui(self):
        try:
            body = UI_FILE.read_bytes()
        except FileNotFoundError:
            self._json(404, {"detail": "UI file not found"})
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _target(self):
        if self.path.startswith("/rag/"):
            return self.rag + self.path[len("/rag"):]
        return self.runtime + self.path

    def _proxy(self):
        data = None
        if self.command in ("POST", "PUT"):
            length = int(self.headers.get("Content-Length", 0) or 0)
            data = self.rfile.read(length) if length else None

        req = urllib.request.Request(self._target(), data=data, method=self.command)
        if data:
            req.add_header("Content-Type", self.headers.get("Content-Type", "application/json"))

        try:
            with urllib.request.urlopen(req, timeout=240) as response:
                body = response.read()
                self.send_response(response.status)
                self.send_header("Content-Type", response.headers.get("Content-Type", "application/json"))
                self._cors()
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
        except urllib.error.HTTPError as exc:
            body = exc.read()
            self.send_response(exc.code)
            self.send_header("Content-Type", exc.headers.get("Content-Type", "application/json"))
            self._cors()
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except Exception as exc:
            self._json(502, {"detail": f"upstream unavailable: {exc}"})

    def _downloads_status(self):
        try:
            files = scan_local_root(self.local_root)
            by_type: Dict[str, int] = {}
            for item in files:
                ext = item["metadata"]["extension"] or "(none)"
                by_type[ext] = by_type.get(ext, 0) + 1
            self._json(200, {
                "source": "downloads",
                "path": str(self.local_root),
                "read_only": True,
                "files": len(files),
                "types": by_type,
                "text_extractable": sum(
                    1 for item in files
                    if item["metadata"]["content_mode"] == "text"
                ),
                "limit": MAX_FILES,
            })
        except Exception as exc:
            self._json(500, {"detail": str(exc)})

    def _downloads_index(self):
        try:
            documents = scan_local_root(self.local_root)
            payload = json.dumps({
                "collection": "downloads",
                "documents": documents,
            }).encode()
            req = urllib.request.Request(
                self.rag + "/v1/ingest/documents",
                data=payload,
                method="POST",
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=240) as response:
                body = json.loads(response.read().decode())
            body["local_source"] = {
                "path": str(self.local_root),
                "read_only": True,
                "files_scanned": len(documents),
            }
            self._json(200, body)
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode(errors="replace")
            try:
                body = json.loads(raw)
            except Exception:
                body = {"detail": raw}
            self._json(exc.code, body)
        except Exception as exc:
            self._json(500, {"detail": str(exc)})

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self._serve_ui()
        elif self.path == "/local/downloads/status":
            self._downloads_status()
        else:
            self._proxy()

    def do_POST(self):
        if self.path == "/local/downloads/index":
            self._downloads_index()
        else:
            self._proxy()

    def do_PUT(self):
        self._proxy()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--runtime", default="http://localhost:8002")
    parser.add_argument("--rag", default="http://localhost:8001")
    parser.add_argument("--local-root", default=str(Path.home() / "Downloads"))
    args = parser.parse_args()

    Handler.runtime = args.runtime.rstrip("/")
    Handler.rag = args.rag.rstrip("/")
    Handler.local_root = Path(args.local_root).expanduser().resolve()

    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"System One UI: http://localhost:{args.port}")
    print(f"Runtime:       {Handler.runtime}")
    print(f"RAG:           {Handler.rag}")
    print(f"Local source:  {Handler.local_root} (read-only)")
    print("Press Ctrl-C to stop.")
    server.serve_forever()


if __name__ == "__main__":
    main()
