from dataclasses import dataclass
from enum import Enum, auto
from ipaddress import IPv4Address, IPv4Network, IPv6Address, IPv6Network
from typing import AbstractSet, Literal, Mapping


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


class Protocol(Enum):
    tcp = auto()
    udp = auto()


class IPver(Enum):
    v4 = auto()
    v6 = auto()


@dataclass(frozen=True)
class PortFwd:
    proto: Protocol
    from_port: int
    to_port: int
    proxy_proto: bool = False
    ip_ver: IPver = IPver.v4


@dataclass(frozen=True)
class Forwards:
    lan: Mapping[str, AbstractSet[PortFwd]]
    guest: Mapping[str, AbstractSet[PortFwd]]
