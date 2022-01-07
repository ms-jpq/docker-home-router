from dataclasses import dataclass
from ipaddress import IPv4Address, IPv6Address
from itertools import chain
from typing import (
    AbstractSet,
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    MutableSet,
    Tuple,
    cast,
)

from std2.ipaddress import IPAddress

from .consts import SERVER_NAME
from .leases import leases
from .options.parser import settings
from .options.types import PortForward, Protocol
from .types import DualStack, Networks


@dataclass(frozen=True)
class _Addrs:
    V4: IPv4Address
    V6: IPv6Address


@dataclass(frozen=True)
class Forwarded:
    TO_NAME: str
    PROTO: Protocol
    FROM_PORT: int
    TO_PORT: int
    TO_ADDR: _Addrs


@dataclass(frozen=True)
class Available:
    NAME: str
    PROTO: Protocol
    PORT: str


def _leased(networks: Networks) -> MutableMapping[str, MutableSet[IPAddress]]:
    leased: MutableMapping[str, MutableSet[IPAddress]] = {}
    for name, addr in leases():
        addrs = leased.setdefault(name, set())
        addrs.add(addr)

    addrs = leased.setdefault(SERVER_NAME, set())
    for addr in cast(
        Iterator[IPAddress],
        (
            next(networks.guest.v4.hosts()),
            next(networks.guest.v6.hosts()),
            next(networks.trusted.v4.hosts()),
            next(networks.trusted.v6.hosts()),
        ),
    ):
        addrs.add(addr)
    return leased


def _pick(
    leased: MutableMapping[str, MutableSet[IPAddress]], stack: DualStack, hostname: str
) -> Tuple[IPv4Address, IPv6Address]:
    lease_addrs = leased.setdefault(hostname, set())
    others = {addr for hn, addrs in leased.items() if hn != hostname for addr in addrs}

    v4 = next(
        chain(
            (addr for addr in lease_addrs if isinstance(addr, IPv4Address)),
            (addr for addr in stack.v4.hosts() if addr not in others),
        )
    )
    v6 = next(
        chain(
            (addr for addr in lease_addrs if isinstance(addr, IPv6Address)),
            (addr for addr in stack.v6.hosts() if addr not in others),
        )
    )

    lease_addrs.add(v4)
    lease_addrs.add(v6)
    return v4, v6


def forwarded_ports(networks: Networks) -> Tuple[AbstractSet[Forwarded]]:
    leased = _leased(networks)

    def cont(
        stack: DualStack, forwards: Mapping[str, AbstractSet[PortForward]]
    ) -> Iterator[Forwarded]:
        for hostname, fws in forwards.items():
            for fwd in fws:
                v4, v6 = _pick(leased, stack=stack, hostname=hostname)
                spec = Forwarded(
                    TO_NAME=hostname,
                    PROTO=fwd.proto,
                    FROM_PORT=fwd.from_port,
                    TO_PORT=fwd.to_port,
                    TO_ADDR=_Addrs(V4=v4, V6=v6),
                )
                yield spec

    fwd = {
        *cont(networks.wireguard, forwards=settings().port_forwards.wireguard),
        *cont(networks.trusted, forwards=settings().port_forwards.trusted),
        *cont(networks.guest, forwards=settings().port_forwards.guest),
    }
    return (fwd,)


def dhcp_fixed(fwds: Iterable[Forwarded]) -> Iterator[Forwarded]:
    seen: MutableSet[str] = set()
    for fwd in fwds:
        name = fwd.TO_NAME
        if name not in seen:
            seen.add(name)
            yield fwd
