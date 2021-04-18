from dataclasses import dataclass
from ipaddress import IPv4Network, IPv6Network
from itertools import chain
from json import loads
from typing import Iterator, Optional, Sequence

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



def _calc_lan_v4(exclusions: str) -> _V4Stack:
    nono = tuple(map(IPv4Network, exclusions.split(LFS)))


def _calc_lan_v6(ula_prefix: Optional[str], ula_subnet: Optional[str]) -> _V6Stack:
    v6_prefix = int(ula_prefix.replace(":", ""), 16)
    v6_subnet = int(ula_subnet.replace(":", ""), 16)
    if not v6_prefix < 2 ** 40:
        raise ValueError()
    elif not v6_subnet < 2 ** 16:
        raise ValueError()

    lan_v6 = f"fd00:{ula_prefix}:{ula_subnet}/64"


def calculate_networks() -> Networks:
    lan = DualStack(v4=IPv4Network(""), v6=IPv6Network(""))
    wireguard = DualStack(v4=IPv4Network(""), v6=IPv6Network(""))
    tor = DualStack(v4=IPv4Network(""), v6=IPv6Network(""))
    guest = DualStack(v4=IPv4Network(""), v6=IPv6Network(""))
    networks = Networks(
        lan=lan,
        wireguard=wireguard,
        tor=tor,
        guest=guest,
    )
    return networks
