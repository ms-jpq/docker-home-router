from ipaddress import ip_address
from os import linesep
from typing import Iterator, Tuple

from std2.types import IPAddress

from .consts import GUEST_IF, LEASES, SERVER_NAME
from .types import Networks


def srv_addrs(networks: Networks) -> Iterator[Tuple[str, IPAddress]]:
    if GUEST_IF:
        yield SERVER_NAME, next(networks.guest.v4.hosts())
        yield SERVER_NAME, next(networks.guest.v6.hosts())
    else:
        yield SERVER_NAME, next(networks.lan.v4.hosts())
        yield SERVER_NAME, next(networks.lan.v6.hosts())


def leases(networks: Networks) -> Iterator[Tuple[str, IPAddress]]:
    LEASES.parent.mkdir(parents=True, exist_ok=True)
    LEASES.touch()
    lines = LEASES.read_text().rstrip().split(linesep)

    yield from srv_addrs(networks)
    for line in reversed(lines):
        lhs, _, rest = line.partition(" ")
        if lhs == "duid":
            pass
        else:
            _, addr, rhs = rest.split(" ", maxsplit=2)
            name, _, _ = rhs.rpartition(" ")
            if name != "*":
                yield name, ip_address(addr)
