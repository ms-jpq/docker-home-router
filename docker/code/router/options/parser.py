from dataclasses import asdict
from functools import cache
from typing import Any, Iterator

from std2.graphlib import merge
from std2.locale import pathsort_key
from std2.pickle.decoder import new_decoder
from yaml import safe_load

from ..consts import CONFIG, DEFAULT_CONFIG
from .types import (
    DHCP,
    DNS,
    Domains,
    GuestAccessible,
    IPv4,
    IPv6,
    PortBindings,
    Settings,
    WireGuard,
    _IPAddresses,
)


def _raw() -> Settings:
    def cont() -> Iterator[Any]:
        for path in sorted(CONFIG.rglob("*.yml"), key=pathsort_key):
            yml = safe_load(path.read_text())
            yield yml

    yml = safe_load(DEFAULT_CONFIG.read_text())
    conf = merge(yml, *cont())
    decoder = new_decoder[Settings](Settings)
    settings = decoder(conf)
    return settings


def encode_dns_name(raw: str) -> str:
    def cont() -> Iterator[str]:
        for char in raw.encode("idna").decode():
            if char.isalnum() or char in {"."}:
                yield char
            else:
                yield "-"

    return "".join(cont())


def _validate_bindings(bindings: PortBindings) -> None:
    ports = asdict(bindings).values()
    min_p, max_p = 1025, 2 ** 16 - 1

    for port in ports:
        assert port >= min_p and port <= max_p

    assert len(ports) == len({*ports})


@cache
def settings() -> Settings:
    raw = _raw()
    _validate_bindings(raw.port_bindings)

    assert 16 <= raw.ip_addresses.ipv4.managed_prefix_len <= 24
    assert 16 <= raw.ip_addresses.ipv4.tor_prefix_len <= 24
    assert 1 <= raw.dhcp.lease_time <= raw.dhcp.lease_time

    settings = Settings(
        interfaces=raw.interfaces,
        ip_addresses=_IPAddresses(
            ipv4=IPv4(
                loopback_exclusions=raw.ip_addresses.ipv4.loopback_exclusions,
                managed_network_exclusions=raw.ip_addresses.ipv4.managed_network_exclusions,
                managed_prefix_len=raw.ip_addresses.ipv4.managed_prefix_len,
                tor_prefix_len=raw.ip_addresses.ipv4.tor_prefix_len,
            ),
            ipv6=IPv6(
                ula_global_prefix=raw.ip_addresses.ipv6.ula_global_prefix,
                prefix_delegation=raw.ip_addresses.ipv6.prefix_delegation,
            ),
        ),
        dhcp=DHCP(
            lease_time=raw.dhcp.lease_time,
        ),
        dns=DNS(
            local_domains=Domains(
                trusted=encode_dns_name(raw.dns.local_domains.trusted),
                wireguard=encode_dns_name(raw.dns.local_domains.wireguard),
                guest=encode_dns_name(raw.dns.local_domains.guest),
            ),
            local_ttl=raw.dns.local_ttl,
            upstream_servers={*map(encode_dns_name, raw.dns.upstream_servers)},
        ),
        wireguard=WireGuard(
            server_name=encode_dns_name(raw.wireguard.server_name),
            peers={*map(encode_dns_name, raw.wireguard.peers)},
        ),
        traffic_control=raw.traffic_control,
        port_bindings=raw.port_bindings,
        port_forwards=raw.port_forwards,
        guest_accessible=GuestAccessible(
            trusted=raw.guest_accessible.trusted,
            wireguard=raw.guest_accessible.wireguard,
        ),
    )
    return settings
