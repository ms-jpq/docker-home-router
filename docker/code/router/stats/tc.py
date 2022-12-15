from os import linesep
from re import compile
from subprocess import check_output
from typing import Iterator

from std2.locale import si_prefixed

from ..cake.main import TC_IFB
from ..consts import SHORT_DURATION
from ..options.parser import settings

_RE_ROW = compile(r"^(?P<header>\s+\w+)(?P<cols>(?:\s+\d+)+)$")
_RE_COLS = compile(r"\s+(?P<quantity>\d+)")


def _parse(raw: str) -> Iterator[str]:
    for line in raw.splitlines():
        if m := _RE_ROW.fullmatch(line):
            yield m.group("header")
            for col in _RE_COLS.finditer(m.group("cols")):
                quantity = int(col.group("quantity"))
                parsed = si_prefixed(quantity)
                yield parsed.rjust(len(col.group()))
        else:
            yield line

        yield linesep


def _feed(if_name: str) -> str:
    raw = check_output(
        ("tc", "-statistics", "qdisc", "show", "dev", if_name),
        text=True,
        timeout=SHORT_DURATION,
    )

    return "".join(_parse(raw))


def feed() -> str:
    raw1, raw2 = _feed(settings().interfaces.wan), _feed(TC_IFB)
    return "-- TX --" + linesep + raw1 + linesep * 3 + "-- RX --" + linesep + raw2
