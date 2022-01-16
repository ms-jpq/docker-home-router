from dataclasses import dataclass
from enum import Enum, auto
from ipaddress import IPv4Network
from typing import AbstractSet, Mapping, Optional, Sequence

from std2.ipaddress import IPAddress


@dataclass(frozen=True)
class Interfaces:
    wan: str
    trusted: str
    wireguard: str
    guest: Optional[str]
    unmanaged: AbstractSet[str]


@dataclass(frozen=True)
class IPv4:
    loopback_exclusions: AbstractSet[IPv4Network]
    managed_network_exclusions: AbstractSet[IPv4Network]
    managed_prefix_len: int
    tor_prefix_len: int


@dataclass(frozen=True)
class IPv6:
    ula_global_prefix: Optional[str]
    prefix_delegation: bool


@dataclass(frozen=True)
class _IPAddresses:
    ipv4: IPv4
    ipv6: IPv6


@dataclass(frozen=True)
class DHCP:
    lease_time: int


@dataclass(frozen=True)
class Domains:
    trusted: str
    wireguard: str
    guest: str


@dataclass(frozen=True)
class Splithorizon:
    trusted: Mapping[str, AbstractSet[str]]
    wireguard: Mapping[str, AbstractSet[str]]
    guest: Mapping[str, AbstractSet[str]]


@dataclass(frozen=True)
class DNS:
    local_domains: Domains
    local_ttl: int
    upstream_servers: AbstractSet[str]
    split_horizon: Splithorizon
    records: Mapping[str, AbstractSet[IPAddress]]


@dataclass(frozen=True)
class WireGuard:
    server_name: str
    peers: AbstractSet[str]


@dataclass(frozen=True)
class TrafficControl:
    transmit: Sequence[str]
    receive: Sequence[str]


@dataclass(frozen=True)
class PortBindings:
    wireguard: int
    squid: int
    tor: int
    statistics: int


class Protocol(Enum):
    tcp = auto()
    udp = auto()


@dataclass(frozen=True)
class Accessible:
    protocols: AbstractSet[Protocol]
    port: int


@dataclass(frozen=True)
class PortForward(Accessible):
    from_port: Optional[int] = None


@dataclass(frozen=True)
class PortForwards:
    trusted: Mapping[str, Sequence[PortForward]]
    wireguard: Mapping[str, Sequence[PortForward]]
    guest: Mapping[str, Sequence[PortForward]]


@dataclass(frozen=True)
class GuestAccessible:
    trusted: Mapping[str, Sequence[Accessible]]
    wireguard: Mapping[str, Sequence[Accessible]]


@dataclass(frozen=True)
class Settings:
    interfaces: Interfaces
    ip_addresses: _IPAddresses

    dhcp: DHCP
    dns: DNS

    wireguard: WireGuard
    traffic_control: TrafficControl

    port_bindings: PortBindings

    port_forwards: PortForwards
    guest_accessible: GuestAccessible
