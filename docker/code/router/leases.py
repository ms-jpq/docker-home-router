from ipaddress import ip_address
from os import linesep
from typing import Iterator, Tuple

from std2.ipaddress import IPAddress

from .consts import LEASES


def leases() -> Iterator[Tuple[str, IPAddress]]:
    LEASES.parent.mkdir(parents=True, exist_ok=True)
    LEASES.touch()
    lines = LEASES.read_text().rstrip().split(linesep)

    for line in reversed(lines):
        if line:
            lhs, _, rest = line.partition(" ")
            if lhs == "duid":
                pass
            else:
                _, addr, rhs = rest.split(" ", maxsplit=2)
                name, _, _ = rhs.rpartition(" ")
                if name != "*":
                    yield name, ip_address(addr)
