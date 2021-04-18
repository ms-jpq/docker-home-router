from ipaddress import IPv4Network
from typing import Iterable, Iterator

from std2.ipaddress import RFC_1918


def _private_subnets(prefix: int) -> Iterator[IPv4Network]:
    for network in RFC_1918:
        try:
            yield from network.subnets(new_prefix=prefix)
        except ValueError:
            pass


def pick_private(existing: Iterable[IPv4Network], prefix: int) -> Iterator[IPv4Network]:
    seen = {*existing}

    for candidate in _private_subnets(prefix):
        for network in seen:
            if not candidate.overlaps(network) and not network.overlaps(candidate):
                seen.add(candidate)
                yield candidate
                break
