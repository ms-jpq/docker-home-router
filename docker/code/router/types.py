from dataclasses import dataclass
from ipaddress import IPv4Address, IPv4Network, IPv6Address, IPv6Network
from typing import Mapping


@dataclass(frozen=True)
class DualStack:
    v4: IPv4Network
    v6: IPv6Network


@dataclass(frozen=True)
class Networks:
    guest: DualStack
    lan: DualStack
    tor: DualStack
    wireguard: DualStack


@dataclass(frozen=True)
class WGPeer:
    v4: IPv4Address
    v6: IPv6Address


WGPeers = Mapping[str, WGPeer]
