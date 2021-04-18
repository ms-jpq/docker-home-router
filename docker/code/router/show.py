from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer, ThreadingHTTPServer
from pathlib import Path
from typing import Callable

from jinja2 import Environment

from .consts import J2
from .render import j2_build, j2_render

Feed = Callable[[], str]

_TPL = Path("show", "index.html")


def _render(j2: Environment, title: str, feed: Feed) -> str:
    body = feed()
    env = {"TITLE": title, "BODY": body}
    page = j2_render(j2, path=_TPL, env=env)
    return page


def _head(
    handler: BaseHTTPRequestHandler, j2: Environment, title: str, feed: Feed
) -> bytes:
    headers = {key.casefold(): val for key, val in handler.headers.items()}
    content_len = int(headers.get("content-length", 0))
    _ = handler.rfile.read(content_len)

    body = _render(j2, title=title, feed=feed).encode()
    handler.send_response(HTTPStatus.OK)
    handler.send_header("Content-Length", value=str(len(body)))
    handler.send_header("Content-Type", value="text/html")
    handler.end_headers()
    return body


def show(title: str, port: int, feed: Feed) -> HTTPServer:
    j2 = j2_build(J2)

    class Handler(BaseHTTPRequestHandler):
        def do_HEAD(self) -> None:
            _head(self, j2=j2, title=title, feed=feed)

        def do_GET(self) -> None:
            body = _head(self, j2=j2, title=title, feed=feed)
            self.wfile.write(body)

    srv = ThreadingHTTPServer(("localhost", port), Handler)
    return srv
