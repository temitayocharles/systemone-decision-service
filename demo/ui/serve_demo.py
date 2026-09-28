#!/usr/bin/env python3
"""Serve the System One workspace and proxy its two local APIs.

The browser uses one origin:
- /health and /v2/* -> System One runtime (default localhost:8002)
- /rag/*            -> RAG service (default localhost:8001), with /rag removed

Run:
    python3 serve_demo.py
    python3 serve_demo.py --port 8080 --runtime http://localhost:8002 --rag http://localhost:8001
"""

from __future__ import annotations

import argparse
import os
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
UI_FILE = os.path.join(HERE, "system-one-demo-ui.html")


class Handler(BaseHTTPRequestHandler):
    runtime = "http://localhost:8002"
    rag = "http://localhost:8001"

    def log_message(self, *args):
        pass

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def _serve_ui(self):
        try:
            with open(UI_FILE, "rb") as handle:
                body = handle.read()
        except FileNotFoundError:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"UI file not found")
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
            req.add_header(
                "Content-Type",
                self.headers.get("Content-Type", "application/json"),
            )

        try:
            with urllib.request.urlopen(req, timeout=240) as response:
                body = response.read()
                self.send_response(response.status)
                self.send_header(
                    "Content-Type",
                    response.headers.get("Content-Type", "application/json"),
                )
                self._cors()
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
        except urllib.error.HTTPError as exc:
            body = exc.read()
            self.send_response(exc.code)
            self.send_header(
                "Content-Type",
                exc.headers.get("Content-Type", "application/json"),
            )
            self._cors()
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except Exception as exc:
            body = ('{"detail":"upstream unavailable: %s"}' % exc).encode()
            self.send_response(502)
            self.send_header("Content-Type", "application/json")
            self._cors()
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self._serve_ui()
        else:
            self._proxy()

    def do_POST(self):
        self._proxy()

    def do_PUT(self):
        self._proxy()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--runtime", default="http://localhost:8002")
    parser.add_argument("--rag", default="http://localhost:8001")
    args = parser.parse_args()

    Handler.runtime = args.runtime.rstrip("/")
    Handler.rag = args.rag.rstrip("/")

    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"System One UI: http://localhost:{args.port}")
    print(f"Runtime:       {Handler.runtime}")
    print(f"RAG:           {Handler.rag}")
    print("Press Ctrl-C to stop.")
    server.serve_forever()


if __name__ == "__main__":
    main()
