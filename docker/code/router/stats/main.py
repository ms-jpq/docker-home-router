from enum import Enum
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path, PurePosixPath
from typing import AbstractSet, Any, Callable, Mapping
from urllib.parse import urlsplit

from py_dev.srv.static import build_j2, get
from std2.pathlib import is_relative_to
from std2.types import never

from ..consts import J2, STATS_PORT
from ..render import j2_build, j2_render
from ..wireguard.main import QR_DIR
from .dhcp import feed as dhcp_feed
from .dns import feed as dns_feed
from .fwds import feed as fwd_feed
from .nft import feed as nft_feed
from .subnets import feed as subnets_feed
from .tc import feed as tc_feed

Feed = Callable[[], str]


_INDEX_TPL = Path("show", "index.html")
_SHOW_TPL = Path("show", "stats.html")


class _Path(Enum):
    index = PurePosixPath("/")
    dhcp = PurePosixPath("/", "dhcp")
    dns = PurePosixPath("/", "dns")
    fwd = PurePosixPath("/", "fwd")
    nft = PurePosixPath("/", "nft")
    subnets = PurePosixPath("/", "subnets")
    tc = PurePosixPath("/", "tc")
    wg = PurePosixPath("/", "wg")


def _route(handler: BaseHTTPRequestHandler) -> _Path:
    path = urlsplit(handler.path).path
    paths: AbstractSet[_Path] = {*_Path} - {_Path.index}
    for candidate in paths:
        if is_relative_to(path, candidate.value):
            return candidate
    else:
        return _Path.index


def _get(handler: BaseHTTPRequestHandler, page: bytes) -> None:
    headers = {key.casefold(): val for key, val in handler.headers.items()}
    content_len = int(headers.get("content-length", 0))
    _ = handler.rfile.read(content_len)

    handler.send_response(HTTPStatus.OK)
    handler.send_header("Content-Length", value=str(len(page)))
    handler.send_header("Content-Type", value="text/html")
    handler.end_headers()
    handler.wfile.write(page)


def main() -> None:
    static_j2 = build_j2()
    j2 = j2_build(J2)

    def http_get(handler: BaseHTTPRequestHandler):
        path = _route(handler)
        if path is _Path.index:
            env: Mapping[str, Any] = {
                "SERVICES": ((path.name, path.value) for path in _Path)
            }
            page = j2_render(j2, path=_INDEX_TPL, env=env).encode()
            _get(handler, page=page)

        elif path is _Path.dhcp:
            env = {"TITLE": path.name, "BODY": dhcp_feed()}
            page = j2_render(j2, path=_SHOW_TPL, env=env).encode()
            _get(handler, page=page)

        elif path is _Path.dns:
            env = {"TITLE": path.name, "BODY": dns_feed()}
            page = j2_render(j2, path=_SHOW_TPL, env=env).encode()
            _get(handler, page=page)

        elif path is _Path.fwd:
            env = {"TITLE": path.name, "BODY": fwd_feed()}
            page = j2_render(j2, path=_SHOW_TPL, env=env).encode()
            _get(handler, page=page)

        elif path is _Path.nft:
            env = {"TITLE": path.name, "BODY": nft_feed()}
            page = j2_render(j2, path=_SHOW_TPL, env=env).encode()
            _get(handler, page=page)

        elif path is _Path.subnets:
            env = {"TITLE": path.name, "BODY": subnets_feed()}
            page = j2_render(j2, path=_SHOW_TPL, env=env).encode()
            _get(handler, page=page)

        elif path is _Path.tc:
            env = {"TITLE": path.name, "BODY": tc_feed()}
            page = j2_render(j2, path=_SHOW_TPL, env=env).encode()
            _get(handler, page=page)

        elif path is _Path.wg:
            get(static_j2, handler=handler, base=_Path.wg.value, root=QR_DIR)

        else:
            never(path)

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            try:
                http_get(self)
            except BrokenPipeError:
                pass

    srv = ThreadingHTTPServer(("", STATS_PORT), Handler)
    srv.serve_forever()
