from ipaddress import ip_address
from multiprocessing import cpu_count
from shutil import copystat
from subprocess import check_call
from typing import Any, Mapping, cast

from std2.pathlib import walk
from std2.types import IPNetwork

from ..consts import (
    DATA,
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
from ..wg import gen_wg, wg_env

_UNBOUND = DATA / "unbound"
_PEM = _UNBOUND / "tls.pem"
_KEY = _UNBOUND / "tls.key"


def _is_ip_addr(srv: str) -> bool:
    try:
        ip_address(srv)
    except ValueError:
        return False
    else:
        return True


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
        dns_addrs = tuple(srv for srv in DNS_SERVERS if _is_ip_addr(srv))
        dns_hosts = tuple(srv for srv in DNS_SERVERS if not _is_ip_addr(srv))
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
            "DNS_ADDRS": dns_addrs,
            "DNS_HOSTS": dns_hosts,
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


def _gen_keys(networks: Networks) -> None:
    _UNBOUND.mkdir(parents=True, exist_ok=True)
    if not _PEM.exists() or not _KEY.exists():
        san = (
            f"IP:{next(cast(IPNetwork,network).hosts())}"
            for network in (
                networks.guest.v4,
                networks.guest.v6,
                networks.lan.v4,
                networks.lan.v6,
                networks.wireguard.v4,
                networks.wireguard.v6,
            )
        )
        check_call(
            (
                "openssl",
                "req",
                "-x509",
                "-newkey",
                "rsa:4096",
                "-sha256",
                "-days",
                "6969",
                "-nodes",
                "-out",
                str(_PEM),
                "-keyout",
                str(_KEY),
                "-subj",
                f"/CN={SERVER_NAME}.{LAN_DOMAIN}",
                "-addext",
                f"subjectAltName={','.join(san)}",
            )
        )


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

    gen_wg(networks)
    _gen_keys(networks)