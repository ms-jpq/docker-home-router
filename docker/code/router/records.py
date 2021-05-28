from ipaddress import IPv4Address, IPv6Address
from itertools import chain
from locale import strxfrm
from typing import Iterator, Mapping, MutableMapping, MutableSet, Sequence, Tuple

from std2.types import IPAddress

from .leases import srv_addrs
from .types import Networks
from .wg import clients


def _p_peers(networks: Networks) -> Iterator[Tuple[str, IPAddress]]:
    for client in clients(networks):
        yield client.name, client.v4.ip
        yield client.name, client.v6.ip


def encode_dns(name: str) -> str:
    def cont() -> Iterator[str]:
        for char in name.encode("idna").decode():
            if char.isalnum():
                yield char
            else:
                yield "-"

    return "".join(cont())


def dns_records(
    networks: Networks,
) -> Mapping[str, Tuple[Sequence[IPv4Address], Sequence[IPv6Address]]]:
    mappings: MutableMapping[str, MutableSet[IPAddress]] = {}
    for name, addr in chain(srv_addrs(networks), _p_peers(networks)):
        acc = mappings.setdefault(name, set())
        acc.add(addr)

    records = {
        encode_dns(key): (
            sorted(i for i in mappings[key] if isinstance(i, IPv4Address)),
            sorted(i for i in mappings[key] if isinstance(i, IPv6Address)),
        )
        for key in sorted(mappings, key=strxfrm)
    }
    return records
