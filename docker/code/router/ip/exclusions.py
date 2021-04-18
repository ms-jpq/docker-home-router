from ipaddress import IPv4Network
from typing import Iterable, Iterator


def private_subnets(prefix: int) -> Iterator[IPv4Network]:
    private_ranges = (
        IPv4Network("192.168.0.0/16"),
        IPv4Network("172.16.0.0/12"),
        IPv4Network("10.0.0.0/8"),
    )
    for network in private_ranges:
        try:
            yield from network.subnets(new_prefix=prefix)
        except ValueError:
            pass


def p_exclusions(
    exclude_from: Iterable[IPv4Network],
    candidates: Iterator[IPv4Network],
) -> Iterator[IPv4Network]:
    seen = {*exclude_from}

    for candidate in candidates:
        for network in seen:
            if not candidate.overlaps(network) and not network.overlaps(candidate):
                seen.add(candidate)
                yield candidate
                break
