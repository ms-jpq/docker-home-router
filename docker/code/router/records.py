from ipaddress import IPv4Address, IPv6Address
from itertools import chain
from json import loads
from locale import strxfrm
from typing import Iterator, Mapping, MutableMapping, MutableSet, Sequence, Tuple
from urllib.parse import quote_plus

from std2.pickle import decode
from std2.pickle.coders import BUILTIN_DECODERS
from std2.types import IPAddress

from .consts import WG_PEERS_JSON
from .leases import srv_addrs
from .types import Networks, WGPeers


def _p_peers() -> Iterator[Tuple[str, IPAddress]]:
    json = loads(WG_PEERS_JSON.read_text())
    peers: WGPeers = decode(WGPeers, json, decoders=BUILTIN_DECODERS)
    for name, addrs in peers.items():
        yield name, addrs.v4
        yield name, addrs.v6


def dns_records(
    networks: Networks,
) -> Mapping[str, Tuple[Sequence[IPv4Address], Sequence[IPv6Address]]]:
    mappings: MutableMapping[str, MutableSet[IPAddress]] = {}
    for name, addr in chain(srv_addrs(networks), _p_peers()):
        acc = mappings.setdefault(name, set())
        acc.add(addr)

    records = {
        quote_plus(key): (
            sorted(i for i in mappings[key] if isinstance(i, IPv4Address)),
            sorted(i for i in mappings[key] if isinstance(i, IPv6Address)),
        )
        for key in sorted(mappings, key=strxfrm)
    }
    return records
