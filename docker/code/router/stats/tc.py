from os import linesep
from subprocess import check_output

from ..cake.main import TC_IFB
from ..consts import SHORT_DURATION
from ..options.parser import settings


def _feed(if_name: str) -> str:
    raw = check_output(
        ("tc", "-statistics", "qdisc", "show", "dev", if_name),
        text=True,
        timeout=SHORT_DURATION,
    )
    return raw.strip()


def feed() -> str:
    raw1, raw2 = _feed(settings().interfaces.wan), _feed(TC_IFB)
    return "-- TX --" + linesep + raw1 + linesep * 3 + "-- RX --" + linesep + raw2
