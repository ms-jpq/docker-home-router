from subprocess import check_output

from ..consts import TIMEOUT


def feed() -> str:
    raw = check_output(
        ("tc", "-statistics", "qdisc", "show"), text=True, timeout=TIMEOUT
    )
    return raw.strip()
