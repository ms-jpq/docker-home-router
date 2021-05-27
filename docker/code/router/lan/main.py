from ipaddress import IPv4Address, IPv6Address
from itertools import chain
from json import loads
from locale import strxfrm
from os import sep
from pathlib import Path
from subprocess import check_call
from time import sleep
from typing import Iterator, Mapping, MutableMapping, MutableSet, Sequence, Tuple

from jinja2 import Environment
from std2.pickle import decode
from std2.pickle.coders import BUILTIN_DECODERS
from std2.types import IPAddress

from ..consts import J2, LAN_DOMAIN, SHORT_DURATION, WG_PEERS_JSON
from ..leases import leases
from ..render import j2_build, j2_render
from ..subnets import load_networks
from ..types import WGPeers

_BASE = Path(sep, "srv", "run", "unbound", "lan")
_DYN = Path("dns", "2-records.conf")
_CONF = _BASE / "1-main.conf"
_RECORDS = _BASE / "2-records.conf"


def _p_peers() -> Iterator[Tuple[str, IPAddress]]:
    WG_PEERS_JSON.parent.mkdir(parents=True, exist_ok=True)
    WG_PEERS_JSON.touch()
    json = loads(WG_PEERS_JSON.read_text() or "{}")
    peers: WGPeers = decode(WGPeers, json, decoders=BUILTIN_DECODERS)
    for name, addrs in peers.items():
        yield name, addrs.v4
        yield name, addrs.v6


def dns_records() -> Mapping[str, Tuple[Sequence[IPv4Address], Sequence[IPv6Address]]]:
    networks = load_networks()
    mappings: MutableMapping[str, MutableSet[IPAddress]] = {}
    for name, addr in chain(leases(networks), _p_peers()):
        acc = mappings.setdefault(name, set())
        acc.add(addr)

    records = {
        key: (
            sorted(i for i in mappings[key] if isinstance(i, IPv4Address)),
            sorted(i for i in mappings[key] if isinstance(i, IPv6Address)),
        )
        for key in sorted(mappings, key=strxfrm)
    }
    return records


def _poll(j2: Environment) -> None:
    existing = _RECORDS.read_text()

    env = {
        "DNS_RECORDS": dns_records(),
        "LAN_DOMAIN": LAN_DOMAIN,
    }
    new = j2_render(j2, path=_DYN, env=env)
    if new != existing:
        check_call(
            ("unbound-control", "-c", str(_CONF), "reload"), timeout=SHORT_DURATION
        )


def main() -> None:
    j2 = j2_build(J2)
    while True:
        _poll(j2)
        sleep(SHORT_DURATION)
