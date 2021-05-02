from ipaddress import IPv4Address, IPv6Address
from itertools import chain
from typing import (
    AbstractSet,
    Any,
    Iterator,
    Mapping,
    MutableMapping,
    MutableSet,
    Sequence,
    Tuple,
    cast,
)

from std2.pickle import decode
from std2.tree import merge
from std2.types import IPAddress
from yaml import safe_load

from .consts import PORT_FWD, SERVER_NAME
from .leases import leases
from .types import DualStack, Forwards, FWDs, Networks, PortFwd


def _mk_spec(
    hostname: str, fwd: PortFwd, v4: IPv4Address, v6: IPv6Address
) -> Mapping[str, Any]:
    spec = {
        "FROM_NAME": hostname,
        "PROTO": fwd.proto.name,
        "FROM_PORT": fwd.from_port,
        "TO_PORT": fwd.to_port,
        "PROXY_PROTO": fwd.proxy_proto,
        "TO_ADDR": {
            "V4": v4,
            "V6": v6,
        },
    }
    return spec


def _leased(networks: Networks) -> MutableMapping[str, MutableSet[IPAddress]]:
    leased: MutableMapping[str, MutableSet[IPAddress]] = {}
    for name, addr in leases(networks):
        addrs = leased.setdefault(name, set())
        addrs.add(addr)

    addrs = leased.setdefault(SERVER_NAME)
    for addr in cast(
        Iterator[IPAddress],
        (
            next(networks.guest.v4.hosts()),
            next(networks.guest.v6.hosts()),
            next(networks.lan.v4.hosts()),
            next(networks.lan.v6.hosts()),
        ),
    ):
        addrs.add(addr)
    return leased


def _pick(
    leased: Mapping[str, AbstractSet[IPAddress]], stack: DualStack, hostname: str
) -> Tuple[IPv4Address, IPv6Address]:
    v4 = next(
        v4_addr
        for v4_addr in chain(
            (
                addr
                for addr in leased.get(hostname, ())
                if isinstance(addr, IPv4Address)
            ),
            stack.v4.hosts(),
        )
        if any(v4_addr in addrs for addrs in leased.values())
    )
    v6 = next(
        v6_addr
        for v6_addr in chain(
            (
                addr
                for addr in leased.get(hostname, ())
                if isinstance(addr, IPv6Address)
            ),
            stack.v6.hosts(),
        )
        if any(v6_addr in addrs for addrs in leased.values())
    )
    return v4, v6


def forwarded_ports(
    networks: Networks,
) -> Iterator[Mapping[str, Any]]:
    PORT_FWD.parent.mkdir(parents=True, exist_ok=True)

    acc: MutableMapping[str, Any] = {"lan": {}, "guest": {}}
    for path in chain(PORT_FWD.glob("*.yaml"), PORT_FWD.glob("*.yml")):
        raw = path.read_text()
        yaml = safe_load(raw)
        acc = merge(acc, yaml)

    forwards: Forwards = decode(Forwards, acc, strict=False)
    leased = _leased(networks)

    def cont(stack: DualStack, forwards: FWDs) -> Iterator[Mapping[str, Any]]:
        for hostname, fws in forwards.items():
            for fw in fws:
                v4, v6 = _pick(leased, stack=stack, hostname=hostname)
                spec = _mk_spec(hostname, fwd=fw, v4=v4, v6=v6)
                yield spec

    yield from cont(networks.guest, forwards=forwards.guest)
    yield from cont(networks.lan, forwards=forwards.lan)


def dhcp_fixed(fwds: Sequence[Mapping[str, Any]]) -> Iterator[Mapping[str, Any]]:
    seen: MutableSet[str] = set()
    for fwd in fwds:
        name = fwd["FROM_NAME"]
        if name not in seen:
            seen.add(name)
            yield fwd
