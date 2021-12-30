from ipaddress import ip_address
from multiprocessing import cpu_count
from shutil import copystat
from socket import getaddrinfo
from subprocess import check_call
from sys import stderr
from typing import Any, Iterator, Mapping, cast

from std2.ipaddress import LINK_LOCAL_V6, PRIVATE_V6, IPAddress, IPNetwork
from std2.pathlib import walk

from ..consts import (
    DATA,
    DHCP_LEASE_TIME,
    DNS_SEC,
    DNS_SERVERS,
    EXPOSE_STATS,
    GUEST_DOMAIN,
    GUEST_IF,
    IPV6_PD,
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
    WG_DOMAIN,
    WG_IF,
    WG_PORT,
)
from ..ip import ipv6_enabled
from ..port_fwd import dhcp_fixed, forwarded_ports
from ..records import wg_records
from ..render import j2_build, j2_render
from ..subnets import calculate_loopback, calculate_networks, load_networks
from ..types import Networks
from ..wg import gen_wg, wg_env

_UNBOUND = DATA / "unbound"
_PEM = _UNBOUND / "tls.pem"
_KEY = _UNBOUND / "tls.key"


def _resolv_addrs() -> Iterator[IPAddress]:
    for srv in DNS_SERVERS:
        try:
            ip = ip_address(srv)
        except ValueError:
            try:
                addr_infos = getaddrinfo(srv, "domain")
            except Exception as e:
                print(e, file=stderr)
            else:
                for _, _, _, _, info in addr_infos:
                    addr, *_ = info
                    ip = ip_address(addr)
                    yield ip
        else:
            yield ip
    else:
        raise RuntimeError("NO DNS SERVERS")


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
            "IPV6_ULA": PRIVATE_V6,
            "PRIVATE_ADDRS": PRIVATE_ADDRS,
            "USER": USER,
            "WAN_IF": WAN_IF,
            "LAN_IF": LAN_IF,
            "GUEST_IF": GUEST_IF,
            "DHCP_LEASE_TIME": DHCP_LEASE_TIME,
            "WG_IF": WG_IF,
            "IPV6_ENABLED": ipv6_enabled(),
            "LINK_LOCAL_V6": LINK_LOCAL_V6,
            "GUEST_NETWORK_V4": networks.guest.v4,
            "GUEST_NETWORK_V6": networks.guest.v6,
            "LAN_NETWORK_V4": networks.lan.v4,
            "LAN_NETWORK_V6": networks.lan.v6,
            "TOR_NETWORK_V4": networks.tor.v4,
            "TOR_NETWORK_V6": networks.tor.v6,
            "WG_NETWORK_V4": networks.wireguard.v4,
            "WG_NETWORK_V6": networks.wireguard.v6,
            "IPV6_PD": IPV6_PD,
            "LOCAL_TTL": LOCAL_TTL,
            "DNS_SEC": DNS_SEC,
            "DNS_ADDRS": _resolv_addrs(),
            "WG_RECORDS": wg_records(networks),
            "SQUID_PORT": SQUID_PORT,
            "TOR_PORT": TOR_PORT,
            "WG_PORT": WG_PORT,
            "STATS_PORT": STATS_PORT,
            "EXPOSE_STATS": EXPOSE_STATS,
            "LOOPBACK_LOCAL": loop_back,
            "LAN_DOMAIN": LAN_DOMAIN,
            "WG_DOMAIN": WG_DOMAIN,
            "GUEST_DOMAIN": GUEST_DOMAIN,
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
                _PEM,
                "-keyout",
                _KEY,
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
