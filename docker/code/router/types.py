from dataclasses import dataclass
from ipaddress import IPv4Network, IPv6Network


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
