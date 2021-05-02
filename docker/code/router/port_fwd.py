from ipaddress import IPv4Address
from itertools import chain
from typing import AbstractSet, Any, Iterator, Mapping, MutableMapping, MutableSet, cast

from std2.pickle import decode
from std2.tree import merge
from std2.types import IPAddress
from yaml import safe_load

from .consts import PORT_FWD, SERVER_NAME
from .leases import leases
from .types import DualStack, Forwards, FWDs, IPver, Networks, PortFwd


def _mk_spec(hostname: str, fwd: PortFwd, addr: IPAddress) -> Mapping[str, Any]:
    spec = {
        "IP_VER": "ip" if isinstance(addr, IPv4Address) else "ip6",
        "FROM_NAME": hostname,
        "PROTO": fwd.proto.name,
        "FROM_PORT": fwd.from_port,
        "TO_PORT": fwd.to_port,
        "PROXY_PROTO": fwd.proxy_proto,
        "TO_ADDR": addr,
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


def _unseen(
    leased: Mapping[str, AbstractSet[IPAddress]], stack: DualStack, ver: IPver
) -> Iterator[IPAddress]:
    for addr in cast(
        Iterator[IPAddress],
        (stack.v4.hosts() if ver is IPver.v4 else stack.v6.hosts()),
    ):
        if not any(addr in addrs for addrs in leased.values()):
            yield addr


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
    seen_hosts: MutableSet[str] = set()

    def cont(stack: DualStack, forwards: FWDs) -> Iterator[Mapping[str, Any]]:
        for hostname, fws in forwards.items():
            for fw in fws:
                unseen = _unseen(leased, stack=stack, ver=fw.ip_ver)
                if hostname not in seen_hosts:
                    seen_hosts.add(hostname)
                    addrs = leased.setdefault(hostname, set())
                    addr = next(iter(addrs), next(unseen))
                    addrs.add(addr)

                    spec = _mk_spec(hostname, fwd=fw, addr=addr)
                    yield spec

    yield from cont(networks.guest, forwards=forwards.guest)
    yield from cont(networks.lan, forwards=forwards.lan)
