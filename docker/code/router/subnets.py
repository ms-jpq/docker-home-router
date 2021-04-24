from dataclasses import dataclass
from ipaddress import IPv4Network, IPv6Network
from itertools import islice
from json import loads
from random import randint
from typing import Iterable, Iterator, Optional

from std2.ipaddress import RFC_1918
from std2.lex import split
from std2.pickle import decode
from std2.pickle.coders import BUILTIN_DECODERS

from .consts import (
    IP4_EXCLUSION,
    IP6_ULA_GLOBAL,
    IP6_ULA_SUBNET_EXCLUSION,
    NETWORKS_JSON,
)
from .types import DualStack, Networks


@dataclass(frozen=True)
class _V4Stack:
    lan: IPv4Network
    wg: IPv4Network
    tor: IPv4Network
    guest: IPv4Network


@dataclass(frozen=True)
class _V6Stack:
    lan: IPv6Network
    wg: IPv6Network
    tor: IPv6Network
    guest: IPv6Network


def load_networks() -> Networks:
    json = loads(NETWORKS_JSON.read_text())
    networks: Networks = decode(Networks, json, decoders=BUILTIN_DECODERS)
    return networks


def _private_subnets(prefix: int) -> Iterator[IPv4Network]:
    for network in RFC_1918:
        for subnet in network.subnets(new_prefix=prefix):
            yield subnet


def _pick_private(
    existing: Iterable[IPv4Network], prefixes: Iterable[int]
) -> Iterator[IPv4Network]:
    seen = {*existing}

    for prefix in prefixes:
        for candidate in _private_subnets(prefix):
            if all(
                not candidate.overlaps(network) and not network.overlaps(candidate)
                for network in seen
            ):
                seen.add(candidate)
                yield candidate
                break


def _v4(exclusions: str) -> _V4Stack:
    nono = map(IPv4Network, split(exclusions))
    lan, wg, tor, guest = _pick_private(nono, prefixes=(24, 24, 16, 24))
    stack = _V4Stack(lan=lan, wg=wg, tor=tor, guest=guest)
    return stack


def _v6(prefix: Optional[str], subnets: Optional[str]) -> _V6Stack:
    if not prefix:
        bits = format(randint(0, 2 ** 40 - 1), "08x")
        prefix = f"{bits[:2]}:{bits[2:6]}:{bits[6:]}"

    org_prefix = f"fd{prefix}"
    org = IPv6Network(f"{org_prefix}::/48")
    seen = {
        IPv6Network(f"{org_prefix}:{subnet}::/64") for subnet in split(subnets or "")
    }
    lan, wg, tor, guest = islice(
        (subnet for subnet in org.subnets(new_prefix=64) if subnet not in seen), 4
    )

    stack = _V6Stack(lan=lan, wg=wg, tor=tor, guest=guest)
    return stack


def calculate_networks() -> Networks:
    v4, v6 = _v4(IP4_EXCLUSION), _v6(IP6_ULA_GLOBAL, IP6_ULA_SUBNET_EXCLUSION)
    networks = Networks(
        lan=DualStack(v4=v4.lan, v6=v6.lan),
        wireguard=DualStack(v4=v4.wg, v6=v6.wg),
        tor=DualStack(v4=v4.tor, v6=v6.tor),
        guest=DualStack(v4=v4.guest, v6=v6.guest),
    )
    return networks
