from dataclasses import dataclass
from ipaddress import IPv4Network, IPv6Network
from json import loads
from typing import Iterable, Iterator, Optional

from std2.ipaddress import RFC_1918
from std2.pickle import decode
from std2.pickle.coders import ipv4_network_decoder, ipv6_network_decoder

from .consts import LFS, NETWORKS
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
    nono = map(IPv4Network, exclusions.split(LFS))
    lan, wg, tor, guest = _pick_private(nono, prefix=24)
    stack = _V4Stack(lan=lan, wg=wg, tor=tor, guest=guest)
    return stack


def _v6(ula_prefix: Optional[str], ula_subnet: Optional[str]) -> _V6Stack:
    prefix = ula_prefix or ""
    subnet = ula_subnet or ""

    org = f"fd00:{prefix}::/80"


def calculate_networks() -> Networks:
    v4, v6 = _v4(""), _v6("", "")
    networks = Networks(
        lan=DualStack(v4=v4.lan, v6=v6.lan),
        wireguard=DualStack(v4=v4.wg, v6=v6.wg),
        tor=DualStack(v4=v4.tor, v6=v6.tor),
        guest=DualStack(v4=v4.guest, v6=v6.guest),
    )
    return networks
