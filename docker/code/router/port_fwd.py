from ipaddress import IPv4Address
from itertools import chain
from typing import (
    Any,
    Iterator,
    Mapping,
    MutableMapping,
    MutableSequence,
    Sequence,
    cast,
)

from std2.pickle import decode
from std2.tree import merge
from std2.types import IPAddress
from yaml import safe_load

from .consts import PORT_FWD
from .leases import leases
from .types import Forwards, IPver, Networks, PortFwd


def _mk_spec(hostname: str, fwd: PortFwd, addr: IPAddress) -> Mapping[str, Any]:
    spec = {
        "IP_VER": "ip" if isinstance(addr, IPv4Address) else "ip6",
        "FROM_NAME": hostname,
        "PROTO": fwd.proto,
        "FROM_PORT": fwd.from_port,
        "TO_PORT": fwd.to_port,
        "PROXY_PROTO": fwd.proxy_proto,
        "TO_ADDR": addr,
    }
    return spec


def forwarded_ports(
    networks: Networks,
) -> Sequence[Mapping[str, Any]]:
    PORT_FWD.parent.mkdir(parents=True, exist_ok=True)

    acc: MutableMapping[str, Any] = {}
    for path in chain(PORT_FWD.glob("*.yaml"), PORT_FWD.glob("*.yml")):
        raw = path.read_text()
        yaml = safe_load(raw)
        acc = merge(acc, yaml)

    forwards: Forwards = decode(Forwards, acc, strict=False)
    nono = {*(addr for _, addr in leases(networks))} | {
        next(networks.guest.v4.hosts()),
        next(networks.guest.v6.hosts()),
        next(networks.lan.v4.hosts()),
        next(networks.lan.v6.hosts()),
    }

    fwds: MutableSequence[Mapping[str, Any]] = []
    for hostname, fws in forwards.guest.items():
        for fw in fws:
            it = cast(
                Iterator[IPAddress],
                (
                    networks.guest.v4.hosts()
                    if fw.ip_ver is IPver.v4
                    else networks.guest.v6.hosts()
                ),
            )
            addr = next(addr for addr in it if addr not in nono)
            nono.add(addr)
            spec = _mk_spec(hostname, fwd=fw, addr=addr)
            fwds.append(spec)

    for hostname, fws in forwards.lan.items():
        for fw in fws:
            it = cast(
                Iterator[IPAddress],
                (
                    networks.lan.v4.hosts()
                    if fw.ip_ver is IPver.v4
                    else networks.lan.v6.hosts()
                ),
            )
            addr = next(addr for addr in it if addr not in nono)
            nono.add(addr)
            spec = _mk_spec(hostname, fwd=fw, addr=addr)
            fwds.append(spec)

    return fwds
