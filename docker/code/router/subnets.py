from dataclasses import dataclass
from ipaddress import IPv4Network, IPv6Network
from itertools import islice
from json import dumps, loads
from random import randint
from typing import Iterable, Iterator, Optional

from std2.ipaddress import RFC_1918
from std2.lex import split
from std2.pickle import decode, encode
from std2.pickle.coders import (
    ipv4_network_decoder,
    ipv4_network_encoder,
    ipv6_network_decoder,
    ipv6_network_encoder,
)

from .consts import IP4_EXCLUSION, IP6_ULA_GLOBAL, IP6_ULA_SUBNET_EXCLUSION, NETWORKS
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
    json = loads(NETWORKS.read_text())
    networks: Networks = decode(
        Networks, json, decoders=(ipv4_network_decoder, ipv6_network_decoder)
    )
    return networks


def dump_networks(networks: Networks) -> None:
    data = encode(networks, encoders=(ipv4_network_encoder, ipv6_network_encoder))
    json = dumps(data, check_circular=False, ensure_ascii=False, indent=2)
    NETWORKS.write_text(json)


def _private_subnets(prefix: int) -> Iterator[IPv4Network]:
    for network in RFC_1918:
        try:
            yield from network.subnets(new_prefix=prefix)
        except ValueError:
            pass


def _pick_private(
    existing: Iterable[IPv4Network], prefix: int
) -> Iterator[IPv4Network]:
    seen = {*existing}

    for candidate in _private_subnets(prefix):
        for network in seen:
            if not candidate.overlaps(network) and not network.overlaps(candidate):
                seen.add(candidate)
                yield candidate
                break


def _v4(exclusions: str) -> _V4Stack:
    nono = map(IPv4Network, split(exclusions))
    lan, wg, tor, guest = islice(_pick_private(nono, prefix=24), 4)
    stack = _V4Stack(lan=lan, wg=wg, tor=tor, guest=guest)
    return stack


def _v6(prefix: Optional[str], subnets: Optional[str]) -> _V6Stack:
    if not prefix:
        bits = format(randint(0, 2 ** 40 - 1), "08x")
        prefix = f"{bits[:2]}:{bits[2:6]}:{bits[6:]}"

    org_prefix = f"fd{prefix}"
    org = IPv6Network(f"{org_prefix}::/48")
    seen = {
        IPv6Network(f"{org_prefix}:{subnet}::/64")
        for subnet in (subnets or "").split("IFS")
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
