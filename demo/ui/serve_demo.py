#!/usr/bin/env python3
"""Serve the System One workspace, proxy APIs, and expose a read-only local source."""

from __future__ import annotations

import argparse
import json
import mimetypes
import threading
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, List

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


def scan_local_root(root: Path) -> List[Dict[str, Any]]:
    if not root.exists() or not root.is_dir():
        raise FileNotFoundError(f"Local source directory not found: {root}")

    files: List[Dict[str, Any]] = []
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
    downloads_job_lock = threading.Lock()
    downloads_job: Dict[str, Any] = {
        "state": "idle",
        "message": "Not started",
        "started_at": None,
        "finished_at": None,
    }

    def log_message(self, *args):
        pass

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _json(self, status: int, payload: Dict[str, Any]):
        body = json.dumps(payload).encode()
        try:
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self._cors()
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            return

    @classmethod
    def _job_snapshot(cls) -> Dict[str, Any]:
        with cls.downloads_job_lock:
            return dict(cls.downloads_job)

    @classmethod
    def _set_job(cls, **values: Any) -> None:
        with cls.downloads_job_lock:
            cls.downloads_job.update(values)

    @classmethod
    def _run_downloads_index(cls) -> None:
        try:
            cls._set_job(state="scanning", message="Scanning Downloads", started_at=time.time(), finished_at=None)
            documents = scan_local_root(cls.local_root)
            cls._set_job(
                state="indexing",
                message=f"Embedding and indexing {len(documents)} files",
                files_scanned=len(documents),
            )
            payload = json.dumps({"collection": "downloads", "documents": documents}).encode()
            req = urllib.request.Request(
                cls.rag + "/v1/ingest/documents",
                data=payload,
                method="POST",
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=1800) as response:
                body = json.loads(response.read().decode())
            cls._set_job(
                state="completed",
                message=f"Indexed {body.get('chunks', 0)} chunks from {len(documents)} files",
                finished_at=time.time(),
                result=body,
                error=None,
            )
        except Exception as exc:
            cls._set_job(
                state="failed",
                message="Downloads indexing failed",
                finished_at=time.time(),
                error=str(exc),
            )

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
                try:
                    self.send_response(response.status)
                    self.send_header("Content-Type", response.headers.get("Content-Type", "application/json"))
                    self._cors()
                    self.send_header("Content-Length", str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)
                except (BrokenPipeError, ConnectionResetError):
                    return
        except urllib.error.HTTPError as exc:
            body = exc.read()
            try:
                self.send_response(exc.code)
                self.send_header("Content-Type", exc.headers.get("Content-Type", "application/json"))
                self._cors()
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            except (BrokenPipeError, ConnectionResetError):
                return
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

    def _downloads_index_start(self):
        snapshot = self._job_snapshot()
        if snapshot.get("state") in {"scanning", "indexing"}:
            self._json(202, snapshot)
            return
        self._set_job(
            state="queued",
            message="Downloads indexing queued",
            started_at=time.time(),
            finished_at=None,
            result=None,
            error=None,
        )
        thread = threading.Thread(target=type(self)._run_downloads_index, daemon=True)
        thread.start()
        self._json(202, self._job_snapshot())

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self._serve_ui()
        elif self.path == "/local/downloads/status":
            self._downloads_status()
        elif self.path == "/local/downloads/index/status":
            self._json(200, self._job_snapshot())
        else:
            self._proxy()

    def do_POST(self):
        if self.path == "/local/downloads/index":
            self._downloads_index_start()
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
