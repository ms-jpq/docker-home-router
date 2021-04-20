from subprocess import check_output

from ..consts import TIMEOUT
from ..show import show

_PORT = 60695
_TITLE = "TC"


def _feed() -> str:
    raw = check_output(
        ("tc", "-statistics", "qdisc", "show"), text=True, timeout=TIMEOUT
    )
    return raw.strip()


def main() -> None:
    srv = show(_TITLE, port=_PORT, feed=_feed)
    srv.serve_forever()
