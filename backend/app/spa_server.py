"""
Lightweight High-Performance SPA Static Server
================================================
Serves SPA builds with automatic HTML5 fallback to index.html.
Can be invoked with:
  python spa_server.py --port 3000 --dir frontend/dist
  python spa_server.py --port 3001 --dir admin/dist
"""

import os
import sys
import argparse
import http.server
import socketserver
import mimetypes

class SPAHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, directory=None, **kwargs):
        self.spa_directory = directory
        super().__init__(*args, directory=directory, **kwargs)

    def do_GET(self):
        # Proxy API and Admin calls to backend if configured
        if self.path.startswith("/api/") or self.path.startswith("/admin/"):
            self._proxy_to_backend("GET")
            return

        # Translate path to filesystem path
        clean_path = self.path.split("?")[0].split("#")[0].lstrip("/")
        full_path = os.path.join(self.spa_directory, clean_path)

        # If file exists and is a file, serve it directly
        if os.path.isfile(full_path):
            return super().do_GET()

        # If it's a directory with index.html, serve it
        if os.path.isdir(full_path) and os.path.isfile(os.path.join(full_path, "index.html")):
            return super().do_GET()

        # SPA Fallback: serve index.html
        index_path = os.path.join(self.spa_directory, "index.html")
        if os.path.isfile(index_path):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            with open(index_path, "rb") as f:
                content = f.read()
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return

        self.send_error(404, "File not found")

    def do_POST(self):
        if self.path.startswith("/api/") or self.path.startswith("/admin/"):
            self._proxy_to_backend("POST")
        else:
            self.send_error(405, "Method Not Allowed")

    def do_PUT(self):
        if self.path.startswith("/api/") or self.path.startswith("/admin/"):
            self._proxy_to_backend("PUT")
        else:
            self.send_error(405, "Method Not Allowed")

    def do_DELETE(self):
        if self.path.startswith("/api/") or self.path.startswith("/admin/"):
            self._proxy_to_backend("DELETE")
        else:
            self.send_error(405, "Method Not Allowed")

    def do_OPTIONS(self):
        if self.path.startswith("/api/") or self.path.startswith("/admin/"):
            self._proxy_to_backend("OPTIONS")
        else:
            self.send_response(200)
            self.end_headers()

    def _proxy_to_backend(self, method):
        import urllib.request
        import urllib.error

        backend_url = f"http://127.0.0.1:8000{self.path}"
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else None

        req_headers = {k: v for k, v in self.headers.items() if k.lower() not in ("host", "content-length")}
        req = urllib.request.Request(backend_url, data=body, headers=req_headers, method=method)

        try:
            with urllib.request.urlopen(req) as resp:
                self.send_response(resp.status)
                for k, v in resp.headers.items():
                    if k.lower() not in ("transfer-encoding", "content-length"):
                        self.send_header(k, v)
                resp_data = resp.read()
                self.send_header("Content-Length", str(len(resp_data)))
                self.end_headers()
                self.wfile.write(resp_data)
        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            for k, v in e.headers.items():
                if k.lower() not in ("transfer-encoding", "content-length"):
                    self.send_header(k, v)
            err_data = e.read()
            self.send_header("Content-Length", str(len(err_data)))
            self.end_headers()
            self.wfile.write(err_data)
        except Exception as ex:
            self.send_response(502)
            self.end_headers()
            self.wfile.write(str(ex).encode("utf-8"))

class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True

def main():
    parser = argparse.ArgumentParser(description="SPA Static File Server")
    parser.add_argument("--port", type=int, default=3000, help="Port to listen on")
    parser.add_argument("--dir", type=str, required=True, help="Directory to serve")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host interface")
    args = parser.parse_args()

    abs_dir = os.path.abspath(args.dir)
    if not os.path.isdir(abs_dir):
        print(f"Error: Directory '{abs_dir}' does not exist.")
        sys.exit(1)

    handler = lambda *h_args, **h_kwargs: SPAHandler(*h_args, directory=abs_dir, **h_kwargs)
    server = ThreadedHTTPServer((args.host, args.port), handler)
    print(f"Serving SPA from '{abs_dir}' on http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()

if __name__ == "__main__":
    main()
