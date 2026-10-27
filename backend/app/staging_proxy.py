"""
Saarthi Local Staging Reverse Proxy Server
============================================
Simulates Nginx reverse proxy behavior locally on port 8080.
Routes by Host header and path:
  - staging.saarthi.trovanetech.com       -> Saarthi App (port 3000)
  - admin-staging.saarthi.trovanetech.com -> Admin Panel (port 3001)
  - api-staging.saarthi.trovanetech.com   -> Backend API (port 8000)
Path fallbacks:
  - /admin/* -> Admin Panel (port 3001)
  - /api/*   -> Backend API (port 8000)
  - /*       -> Saarthi App (port 3000)
"""

import sys
import os
import http.server
import urllib.request
import urllib.error
import urllib.parse
import socketserver
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [STAGING-PROXY] %(message)s")
logger = logging.getLogger("staging_proxy")

PORT_BACKEND = 8000
PORT_APP = 3000
PORT_ADMIN = 3001
PROXY_PORT = 8080

class StagingProxyHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        logger.info("%s - %s", self.client_address[0], format % args)

    def do_GET(self):
        self._proxy_request("GET")

    def do_POST(self):
        self._proxy_request("POST")

    def do_PUT(self):
        self._proxy_request("PUT")

    def do_DELETE(self):
        self._proxy_request("DELETE")

    def do_OPTIONS(self):
        self._proxy_request("OPTIONS")

    def do_PATCH(self):
        self._proxy_request("PATCH")

    def _determine_target_port(self) -> int:
        host = self.headers.get("Host", "").lower().split(":")[0]
        path = self.path.lower()

        # 1. Host-based routing (matches staging domains)
        if host in ("admin-staging.saarthi.trovanetech.com", "admin.localhost") or host.startswith("admin-staging"):
            if path.startswith("/admin/") or path.startswith("/api/"):
                return PORT_BACKEND
            return PORT_ADMIN
        
        if host in ("api-staging.saarthi.trovanetech.com", "api.localhost") or host.startswith("api-staging"):
            return PORT_BACKEND

        if host in ("staging.saarthi.trovanetech.com", "staging.localhost") or host.startswith("staging"):
            if path.startswith("/api/"):
                return PORT_BACKEND
            return PORT_APP

        # 2. Path-based routing fallback for localhost:8080
        if path.startswith("/api/"):
            return PORT_BACKEND
        if path == "/admin" or path.startswith("/admin/"):
            return PORT_ADMIN
        return PORT_APP

    def _proxy_request(self, method: str):
        target_port = self._determine_target_port()
        target_url = f"http://127.0.0.1:{target_port}{self.path}"

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else None

        # Build outbound headers
        req_headers = {}
        for key, val in self.headers.items():
            if key.lower() not in ("host", "content-length"):
                req_headers[key] = val
        req_headers["Host"] = f"127.0.0.1:{target_port}"
        req_headers["X-Forwarded-For"] = self.client_address[0]
        req_headers["X-Forwarded-Proto"] = "http"
        req_headers["X-Forwarded-Host"] = self.headers.get("Host", "localhost")

        req = urllib.request.Request(target_url, data=body, headers=req_headers, method=method)

        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                self.send_response(resp.status)
                for header_name, header_val in resp.headers.items():
                    if header_name.lower() not in ("transfer-encoding", "content-length"):
                        self.send_header(header_name, header_val)
                resp_data = resp.read()
                self.send_header("Content-Length", str(len(resp_data)))
                self.end_headers()
                self.wfile.write(resp_data)
        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            for header_name, header_val in e.headers.items():
                if header_name.lower() not in ("transfer-encoding", "content-length"):
                    self.send_header(header_name, header_val)
            err_data = e.read()
            self.send_header("Content-Length", str(len(err_data)))
            self.end_headers()
            self.wfile.write(err_data)
        except Exception as exc:
            self.send_response(502)
            self.send_header("Content-Type", "application/json")
            err_body = f'{{"error": "Staging Bad Gateway", "target_port": {target_port}, "detail": "{str(exc)}"}}\n'.encode("utf-8")
            self.send_header("Content-Length", str(len(err_body)))
            self.end_headers()
            self.wfile.write(err_body)

class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True

def main():
    server = ThreadedHTTPServer(("0.0.0.0", PROXY_PORT), StagingProxyHandler)
    logger.info(f"Saarthi Staging Reverse Proxy started on port {PROXY_PORT}")
    logger.info(f"  - Saarthi App Upstream:    http://127.0.0.1:{PORT_APP}")
    logger.info(f"  - Admin Panel Upstream:    http://127.0.0.1:{PORT_ADMIN}")
    logger.info(f"  - Backend API Upstream:    http://127.0.0.1:{PORT_BACKEND}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Stopping Staging Reverse Proxy...")
        server.shutdown()

if __name__ == "__main__":
    main()
