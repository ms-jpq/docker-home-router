from os import linesep
from subprocess import check_output
from typing import Iterator

from ..consts import SHORT_DURATION


def _feeds() -> Iterator[str]:
    yield check_output(("chronyc", "sources"), text=True, timeout=SHORT_DURATION)
    yield check_output(("chronyc", "tracking"), text=True, timeout=SHORT_DURATION)
    yield check_output(("chronyc", "serverstats"), text=True, timeout=SHORT_DURATION)


def feed() -> str:
    return (linesep * 3).join(_feeds())
