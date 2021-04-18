from os import linesep

from ...show import show
from ..consts import DYN, LEASES

_PORT = 60693
_TITLE = "LEASES"


def _feed() -> str:
    dyn, leases = DYN.read_text(), LEASES.read_text()
    return dyn + linesep * 3 + leases


def main() -> None:
    srv = show(_TITLE, port=_PORT, feed=_feed)
    srv.serve_forever()
