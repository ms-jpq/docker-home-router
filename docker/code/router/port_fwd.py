from ipaddress import IPv4Address
from itertools import chain
from typing import Any, Iterator, Mapping, MutableMapping, cast

from std2.pickle import decode
from std2.tree import merge
from std2.types import IPAddress
from yaml import safe_load

from .consts import PORT_FWD
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
    leased = {name: addr for name, addr in leases(networks)}
    nono = {*leased.values()} | {
        next(networks.guest.v4.hosts()),
        next(networks.guest.v6.hosts()),
        next(networks.lan.v4.hosts()),
        next(networks.lan.v6.hosts()),
    }

    def cont(stack: DualStack, forwards: FWDs) -> Iterator[Mapping[str, Any]]:
        for hostname, fws in forwards.items():
            for fw in fws:
                it = (
                    addr
                    for addr in cast(
                        Iterator[IPAddress],
                        (
                            stack.v4.hosts()
                            if fw.ip_ver is IPver.v4
                            else stack.v6.hosts()
                        ),
                    )
                    if addr not in nono
                )
                addr = leased.setdefault(hostname, next(it))
                if addr not in nono:
                    nono.add(addr)
                    spec = _mk_spec(hostname, fwd=fw, addr=addr)
                    yield spec

    yield from cont(networks.guest, forwards=forwards.guest)
    yield from cont(networks.lan, forwards=forwards.lan)
