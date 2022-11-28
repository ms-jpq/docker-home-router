from os import linesep
from subprocess import check_output
from typing import Iterator


def _feeds() -> Iterator[str]:
    yield check_output(("chronyc", "sources"), text=True)
    yield check_output(("chronyc", "tracking"), text=True)
    yield check_output(("chronyc", "serverstats"), text=True)


def feed() -> str:
    return (linesep * 3).join(_feeds())
