from multiprocessing import cpu_count
from shutil import copystat
from typing import Any, Mapping

from std2.pathlib import walk

from ..consts import (
    DHCP_LEASE_TIME,
    DNS_SERVERS,
    DNSSEC,
    GUEST_IF,
    LAN_DOMAIN,
    LAN_IF,
    LOCAL_TTL,
    PRIVATE_ADDRS,
    RUN,
    SERVER_NAME,
    SQUID_PORT,
    STATS_PORT,
    TEMPLATES,
    TOR_PORT,
    USER,
    WAN_IF,
    WG_IF,
    WG_PORT,
)
from ..ip import ipv6_enabled
from ..port_fwd import dhcp_fixed, forwarded_ports
from ..records import dns_records
from ..render import j2_build, j2_render
from ..subnets import calculate_loopback, calculate_networks, load_networks
from ..types import Networks
from ..wg import gen_qr, wg_env


def _env(networks: Networks) -> Mapping[str, Any]:
    if not WAN_IF:
        raise ValueError("WAN_IF - required")
    elif not LAN_IF:
        raise ValueError("LAN_IF - required")
    elif not WG_IF:
        raise ValueError("WG_IF - required")
    else:
        fwds = tuple(forwarded_ports(networks))
        loop_back = calculate_loopback()
        env = {
            "CPU_COUNT": cpu_count(),
            "SERVER_NAME": SERVER_NAME,
            "PRIVATE_ADDRS": PRIVATE_ADDRS,
            "USER": USER,
            "WAN_IF": WAN_IF,
            "LAN_IF": LAN_IF,
            "GUEST_IF": GUEST_IF,
            "DHCP_LEASE_TIME": DHCP_LEASE_TIME,
            "WG_IF": WG_IF,
            "IPV6_ENABLED": ipv6_enabled(),
            "GUEST_NETWORK_V4": networks.guest.v4,
            "GUEST_NETWORK_V6": networks.guest.v6,
            "LAN_NETWORK_V4": networks.lan.v4,
            "LAN_NETWORK_V6": networks.lan.v6,
            "TOR_NETWORK_V4": networks.tor.v4,
            "TOR_NETWORK_V6": networks.tor.v6,
            "WG_NETWORK_V4": networks.wireguard.v4,
            "WG_NETWORK_V6": networks.wireguard.v6,
            "LOCAL_TTL": LOCAL_TTL,
            "DNSSEC": DNSSEC,
            "DNS_SERVERS": DNS_SERVERS,
            "DNS_RECORDS": dns_records(networks),
            "SQUID_PORT": SQUID_PORT,
            "TOR_PORT": TOR_PORT,
            "WG_PORT": WG_PORT,
            "STATS_PORT": STATS_PORT,
            "LOOPBACK_LOCAL": loop_back,
            "LAN_DOMAIN": LAN_DOMAIN,
            "FORWARDED_PORTS": fwds,
            "DHCP_FIXED": dhcp_fixed(fwds),
            "WG": wg_env(networks),
        }
        return env


def main() -> None:
    try:
        networks = load_networks()
    except Exception:
        networks = calculate_networks()

    env = _env(networks)
    j2 = j2_build(TEMPLATES)
    for path in walk(TEMPLATES):
        tpl = path.relative_to(TEMPLATES)
        dest = (RUN / tpl).resolve()
        dest.parent.mkdir(parents=True, exist_ok=True)
        if path.is_symlink():
            dest.unlink(missing_ok=True)
            dest.symlink_to(path.resolve())
        else:
            text = j2_render(j2, path=tpl, env=env)
            dest.write_text(text)
            copystat(path, dest)

    gen_qr(networks)
