from os import linesep
from pathlib import Path
from subprocess import check_call
from time import sleep
from typing import Iterator, Tuple

from jinja2 import Environment

from ...consts import J2, RUN
from ...render import j2_build, j2_render
from ..consts import LEASES

_DYN = RUN / "dnsmasq" / "lan" / "5-dyn.conf"
_TPL = Path("dnsmasq", "5-dyn.conf")
_PID_FILE = Path("/", "var", "run", "dnsmsaq-lan.pid")


def _p_leases() -> Iterator[Tuple[str, str]]:
    lines = LEASES.read_text().rstrip().split(linesep)
    for line in lines:
        yield line, line


def _forever(j2: Environment) -> None:
    dyn = _DYN.read_text()

    mappings = _p_leases()
    env = {"MAPPINGS": mappings}
    text = j2_render(j2, path=_TPL, env=env)

    if dyn != text:
        _DYN.write_text(text)

        pid = _PID_FILE.read_text().rstrip()
        check_call(("kill", pid))


def main() -> None:
    j2 = j2_build(J2)
    while True:
        LEASES.parent.mkdir(parents=True, exist_ok=True)
        LEASES.touch()
        _forever(j2)
        sleep(2)
