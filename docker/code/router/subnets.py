from dataclasses import dataclass
from ipaddress import IPv4Network, IPv6Network
from json import loads
from typing import Optional

from std2.pickle import decode
from std2.pickle.coders import ipv4_network_decoder, ipv6_network_decoder

from .consts import LFS, NETWORKS
from .ip.v4 import pick_private
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


def _v4(exclusions: str) -> _V4Stack:
    nono = map(IPv4Network, exclusions.split(LFS))
    lan, wg, tor, guest = pick_private(nono, prefix=24)
    stack = _V4Stack(lan=lan, wg=wg, tor=tor, guest=guest)
    return stack


def _v6(ula_prefix: Optional[str], ula_subnet: Optional[str]) -> _V6Stack:
    v6_prefix = int(ula_prefix.replace(":", ""), 16)
    v6_subnet = int(ula_subnet.replace(":", ""), 16)
    if not v6_prefix < 2 ** 40:
        raise ValueError()
    elif not v6_subnet < 2 ** 16:
        raise ValueError()

    lan_v6 = f"fd00:{ula_prefix}:{ula_subnet}/64"


def calculate_networks() -> Networks:
    v4, v6 = _v4(""), _v6("", "")
    networks = Networks(
        lan=DualStack(v4=v4.lan, v6=v6.lan),
        wireguard=DualStack(v4=v4.wg, v6=v6.wg),
        tor=DualStack(v4=v4.tor, v6=v6.tor),
        guest=DualStack(v4=v4.guest, v6=v6.guest),
    )
    return networks
