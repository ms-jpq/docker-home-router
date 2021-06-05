from os import linesep
from subprocess import check_output

from ..consts import SHORT_DURATION, TC_IFB, WAN_IF


def _feed(if_name: str) -> str:
    raw = check_output(
        ("tc", "-statistics", "qdisc", "show", "dev", if_name),
        text=True,
        timeout=SHORT_DURATION,
    )
    return raw.strip()


def feed() -> str:
    raw1, raw2 = _feed(WAN_IF), _feed(TC_IFB)
    return "-- TX --" + linesep + raw1 + linesep * 3 + "-- RX --" + linesep + raw2
