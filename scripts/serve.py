#!/usr/bin/env python3
"""Serve data/ over HTTP with CORS, so a locally running app can load this catalog.

Usage: python3 scripts/serve.py [port] [address]   (defaults 8001, 127.0.0.1; use 0.0.0.0 inside a container)
Then open the app with ?catalog=http://localhost:8001/
Development only; the published catalog is served by GitHub.
"""
import functools
import http.server
import pathlib
import sys

DATA_DIR = pathlib.Path(__file__).resolve().parent.parent / 'data'


class CORSHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        # Always serve the current files, so catalog edits show up on reload.
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8001
    address = sys.argv[2] if len(sys.argv) > 2 else '127.0.0.1'
    handler = functools.partial(CORSHandler, directory=str(DATA_DIR))
    with http.server.ThreadingHTTPServer((address, port), handler) as server:
        print(f'Serving {DATA_DIR} at http://localhost:{port}/')
        server.serve_forever()


if __name__ == '__main__':
    main()
