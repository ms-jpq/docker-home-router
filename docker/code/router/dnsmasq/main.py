from ipaddress import ip_address
from itertools import chain
from json import loads
from os import linesep
from pathlib import Path
from subprocess import check_call
from time import sleep
from typing import Iterator, MutableMapping, MutableSet, Optional, Tuple

from jinja2 import Environment
from std2.pickle import decode
from std2.pickle.coders import BUILTIN_DECODERS
from std2.types import IPAddress

from ..consts import ADDN_HOSTS, DYN, J2, LEASES, SERVER_NAME, WG_PEERS_JSON
from ..render import j2_build, j2_render
from ..subnets import load_networks
from ..types import WGPeers

_DYN = Path("dns", "5-dyn.conf")
_ADDN_HOSTS = Path("dns", "5-mappings.conf")
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

    networks = load_networks()
    yield SERVER_NAME, next(networks.lan.v4.hosts())
    yield SERVER_NAME, next(networks.lan.v6.hosts())
    yield SERVER_NAME, next(networks.wireguard.v4.hosts())
    yield SERVER_NAME, next(networks.wireguard.v6.hosts())

    for line in lines:
        if line:
            try:
                _, _, addr, rhs = line.split(" ", maxsplit=3)
            except ValueError:
                pass
            else:
                name, _, _ = rhs.rpartition(" ")
                if name != "*":
                    yield name, ip_address(addr)


def _p_peers() -> Iterator[Tuple[str, IPAddress]]:
    WG_PEERS_JSON.parent.mkdir(parents=True, exist_ok=True)
    WG_PEERS_JSON.touch()
    json = loads(WG_PEERS_JSON.read_text() or "{}")
    peers: WGPeers = decode(WGPeers, json, decoders=BUILTIN_DECODERS)
    for name, addrs in peers.items():
        yield name, addrs.v4
        yield name, addrs.v6


def _forever(j2: Environment) -> None:
    dyn = DYN.read_text()
    addn = ADDN_HOSTS.read_text()
    pid = _pid()

    mappings: MutableMapping[str, MutableSet[IPAddress]] = {}
    for name, addr in chain(_p_leases(), _p_peers()):
        acc = mappings.setdefault(name, set())
        acc.add(addr)

    env = {"MAPPINGS": mappings}
    t1 = j2_render(j2, path=_DYN, env=env)
    t2 = j2_render(j2, path=_ADDN_HOSTS, env=env)

    if pid and (dyn != t1 or addn != t2):
        DYN.write_text(t1)
        ADDN_HOSTS.write_text(t2)
        check_call(("kill", str(pid)))


def main() -> None:
    j2 = j2_build(J2)
    while True:
        _forever(j2)
        sleep(2)
