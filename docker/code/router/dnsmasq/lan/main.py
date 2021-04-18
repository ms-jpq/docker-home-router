from ipaddress import IPv4Address
from os import linesep
from pathlib import Path
from subprocess import check_call
from time import sleep
from typing import Iterator, Optional, Tuple

from jinja2 import Environment
from std2.types import IPAddress

from ...consts import J2
from ...render import j2_build, j2_render
from ..consts import DYN, LEASES

_TPL = Path("dns", "5-dyn.conf")
_PID_FILE = Path("/", "var", "run", "dnsmsaq-lan.pid")


def _pid() -> Optional[int]:
    try:
        pid = _PID_FILE.read_text().rstrip()
    except Exception:
        return None
    else:
        return int(pid)


def _p_leases() -> Iterator[Tuple[str, IPAddress]]:
    LEASES.parent.mkdir(parents=True, exist_ok=True)
    LEASES.touch()
    lines = LEASES.read_text().rstrip().split(linesep)

    for line in lines:
        if line:
            try:
                _, _, ipv4, rhs = line.split(" ", maxsplit=4)
            except ValueError:
                pass
            else:
                name, _, _ = rhs.rpartition(" ")
                yield name, IPv4Address(ipv4)


def _forever(j2: Environment) -> None:
    dyn = DYN.read_text()
    pid = _pid()

    mappings = _p_leases()
    env = {"MAPPINGS": mappings}
    text = j2_render(j2, path=_TPL, env=env)

    if pid and dyn != text:
        DYN.write_text(text)
        check_call(("kill", str(pid)))


def main() -> None:
    j2 = j2_build(J2)
    while True:
        _forever(j2)
        sleep(2)
