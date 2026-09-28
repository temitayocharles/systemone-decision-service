#!/usr/bin/env python3
"""Serve the System One demo UI and proxy API calls to the runtime.

Why this exists: browsers block cross-origin POSTs, and the runtime does
not ship CORS headers. This tiny server (stdlib only) serves the UI at /
and forwards /health and /v2/* to the runtime on localhost:8002, same
origin, so everything just works.

Run:
    python3 serve_demo.py [--port 8080] [--runtime http://localhost:8002]

Then open http://localhost:8080 in a browser.
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

    def log_message(self, *args):  # quieter logs
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
            with open(UI_FILE, "rb") as f:
                body = f.read()
        except FileNotFoundError:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"UI file not found next to serve_demo.py")
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _proxy(self):
        data = None
        if self.command in ("POST", "PUT"):
            length = int(self.headers.get("Content-Length", 0) or 0)
            data = self.rfile.read(length) if length else None
        req = urllib.request.Request(
            self.runtime + self.path, data=data, method=self.command
        )
        if data:
            req.add_header(
                "Content-Type",
                self.headers.get("Content-Type", "application/json"),
            )
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                body = r.read()
                self.send_response(r.status)
                self.send_header(
                    "Content-Type",
                    r.headers.get("Content-Type", "application/json"),
                )
                self._cors()
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
        except urllib.error.HTTPError as e:
            # Pass 4xx/5xx through untouched: the 422 and 502 demos
            # depend on seeing the real status codes.
            body = e.read()
            self.send_response(e.code)
            self.send_header("Content-Type", "application/json")
            self._cors()
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except Exception as e:  # runtime down
            body = ('{"error": "runtime unreachable: %s"}' % e).encode()
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
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8080)
    ap.add_argument("--runtime", default="http://localhost:8002")
    args = ap.parse_args()
    Handler.runtime = args.runtime.rstrip("/")
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"Demo UI:  http://localhost:{args.port}")
    print(f"Runtime:  {Handler.runtime}")
    print("Press Ctrl-C to stop.")
    server.serve_forever()


if __name__ == "__main__":
    main()
