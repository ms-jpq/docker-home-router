from dataclasses import dataclass
from enum import Enum, auto
from ipaddress import IPv4Network, IPv6Network
from typing import AbstractSet, Mapping


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


class Protocol(Enum):
    tcp = auto()
    udp = auto()


@dataclass(frozen=True)
class PortFwd:
    proto: Protocol
    from_port: int
    to_port: int
    proxy_proto: bool = False


FWDs = Mapping[str, AbstractSet[PortFwd]]


@dataclass(frozen=True)
class Forwards:
    lan: FWDs
    guest: FWDs
