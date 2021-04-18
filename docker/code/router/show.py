from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer, ThreadingHTTPServer
from typing import Callable


def _head(self: BaseHTTPRequestHandler, feed: Callable[[], str]) -> bytes:
    headers = {key.casefold(): val for key, val in self.headers.items()}
    content_len = int(headers.get("content-length", 0))
    _ = self.rfile.read(content_len)

    body = feed().encode()
    self.send_response(HTTPStatus.OK)
    self.send_header("Content-Length", value=str(len(body)))
    self.send_header("Content-Type", value="text/html")
    self.end_headers()
    return body


def show(port: int, feed: Callable[[], str]) -> HTTPServer:
    class Handler(BaseHTTPRequestHandler):
        def do_HEAD(self) -> None:
            _head(self, feed=feed)

        def do_GET(self) -> None:
            body = _head(self, feed=feed)
            self.wfile.write(body)

    srv = ThreadingHTTPServer(("localhost", port), Handler)
    return srv
