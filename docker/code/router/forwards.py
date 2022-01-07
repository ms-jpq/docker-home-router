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
    Sequence,
    Tuple,
    cast,
)

from std2.ipaddress import IPAddress

from .consts import SERVER_NAME
from .leases import leases
from .options.parser import settings
from .options.types import Accessible, PortForward, Protocol
from .types import DualStack, Networks


@dataclass(frozen=True)
class _Addrs:
    V4: IPv4Address
    V6: IPv6Address


@dataclass(frozen=True)
class _Dest:
    NAME: str
    PROTO: Protocol
    PORT: int
    ADDR: _Addrs


@dataclass(frozen=True)
class Forwarded(_Dest):
    FROM_PORT: int


@dataclass(frozen=True)
class Available(_Dest):
    ...


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


def forwarded_ports(
    networks: Networks,
) -> Tuple[AbstractSet[Forwarded], AbstractSet[Available]]:
    leased = _leased(networks)

    def c1(
        stack: DualStack, forwards: Mapping[str, Sequence[PortForward]]
    ) -> Iterator[Forwarded]:
        for hostname, fws in forwards.items():
            for fwd in fws:
                for proto in fwd.protocols:
                    v4, v6 = _pick(leased, stack=stack, hostname=hostname)
                    spec = Forwarded(
                        NAME=hostname,
                        PROTO=proto,
                        FROM_PORT=fwd.from_port or fwd.port,
                        PORT=fwd.port,
                        ADDR=_Addrs(V4=v4, V6=v6),
                    )
                    yield spec

    def c2(
        stack: DualStack, available: Mapping[str, Sequence[Accessible]]
    ) -> Iterator[Available]:
        for hostname, accessible in available.items():
            for acc in accessible:
                for proto in acc.protocols:
                    v4, v6 = _pick(leased, stack=stack, hostname=hostname)
                    spec = Available(
                        NAME=hostname,
                        PROTO=proto,
                        PORT=acc.port,
                        ADDR=_Addrs(V4=v4, V6=v6),
                    )
                    yield spec

    fwd = {
        *c1(networks.wireguard, forwards=settings().port_forwards.wireguard),
        *c1(networks.trusted, forwards=settings().port_forwards.trusted),
        *c1(networks.guest, forwards=settings().port_forwards.guest),
    }
    available = {
        *c2(networks.wireguard, available=settings().guest_accessible.wireguard),
        *c2(networks.trusted, available=settings().guest_accessible.trusted),
    }
    return fwd, available


def dhcp_fixed(fwds: Iterable[Forwarded]) -> Iterator[Forwarded]:
    seen: MutableSet[str] = set()
    for fwd in fwds:
        name = fwd.NAME
        if name not in seen:
            seen.add(name)
            yield fwd
