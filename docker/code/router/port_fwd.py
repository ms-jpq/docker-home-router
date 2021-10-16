from ipaddress import IPv4Address, IPv6Address
from itertools import chain
from typing import (
    Any,
    Iterator,
    Mapping,
    MutableMapping,
    MutableSet,
    Sequence,
    Tuple,
    cast,
)

from std2.graphlib import merge
from std2.ipaddress import IPAddress
from std2.locale import pathsort_key
from std2.pickle.decoder import new_decoder
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


def forwarded_ports(networks: Networks) -> Iterator[Mapping[str, Any]]:
    PORT_FWD.mkdir(parents=True, exist_ok=True)

    acc: MutableMapping[str, Any] = {"lan": {}, "guest": {}}
    paths = sorted(
        chain(PORT_FWD.glob("*.yaml"), PORT_FWD.glob("*.yml")),
        key=pathsort_key,
    )
    for path in paths:
        raw = path.read_text()
        yaml = safe_load(raw)
        acc = merge(acc, yaml)

    forwards = new_decoder[Forwards](Forwards, strict=False)(acc)
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
