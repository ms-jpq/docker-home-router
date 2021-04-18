from ipaddress import IPv4Address
from itertools import chain
from json import loads
from os import linesep
from pathlib import Path
from subprocess import check_call
from time import sleep
from typing import Iterator, Optional, Tuple

from jinja2 import Environment
from std2.pickle import decode
from std2.pickle.coders import ipv4_network_decoder, ipv6_network_decoder
from std2.types import IPAddress

from ...consts import J2, WG_PEERS_JSON
from ...render import j2_build, j2_render
from ...types import WGPeers
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


def _p_peers() -> Iterator[Tuple[str, IPAddress]]:
    WG_PEERS_JSON.parent.mkdir(parents=True, exist_ok=True)
    WG_PEERS_JSON.touch()
    json = loads(WG_PEERS_JSON.read_text() or "{}")
    peers: WGPeers = decode(
        WGPeers, json, decoders=(ipv4_network_decoder, ipv6_network_decoder)
    )
    for name, addrs in peers.items():
        yield name, addrs.v4
        yield name, addrs.v6


def _forever(j2: Environment) -> None:
    dyn = DYN.read_text()
    pid = _pid()

    mappings = chain(_p_leases(), _p_peers())
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
