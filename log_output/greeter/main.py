import os
from http.server import BaseHTTPRequestHandler, HTTPServer

GREETING = os.getenv("GREETING", "hello")


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = GREETING.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main():
    port = int(os.getenv("PORT", "3000"))
    print(f"Server started in port {port}", flush=True)
    HTTPServer(("", port), Handler).serve_forever()


if __name__ == "__main__":
    main()
