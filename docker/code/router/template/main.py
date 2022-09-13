from dataclasses import dataclass
from ipaddress import IPv4Address, ip_address
from itertools import chain
from multiprocessing import cpu_count
from pprint import pformat
from shutil import copystat, get_terminal_size
from socket import getaddrinfo
from subprocess import check_call
from sys import stderr
from textwrap import dedent
from typing import (
    AbstractSet,
    Any,
    Iterable,
    Iterator,
    Mapping,
    MutableSet,
    Tuple,
    cast,
)

from std2.ipaddress import (
    LINK_LOCAL_V6,
    LOOPBACK_V4,
    LOOPBACK_V6,
    PRIVATE_V6,
    IPAddress,
    IPNetwork,
)
from std2.pathlib import walk

from ..consts import DATA, PRIVATE_ADDRS, RUN, SERVER_NAME, TEMPLATES, USER
from ..forwards import Split, dhcp_fixed, forwarded_ports
from ..ip import ipv6_enabled
from ..options.parser import settings
from ..records import wg_records
from ..render import j2_build, j2_render
from ..subnets import calculate_loopback, calculate_networks, load_networks
from ..types import Networks
from ..wg import gen_wg, wg_env

_UNBOUND = DATA / "unbound"
_PEM = _UNBOUND / "tls.pem"
_KEY = _UNBOUND / "tls.key"


@dataclass(frozen=True)
class _DNS_Record:
    ADDR: IPAddress
    NAME: str
    TYPE: str


def _resolv_addrs() -> Iterator[Tuple[IPAddress, int]]:
    srvs = settings().dns.upstream_servers
    seen: MutableSet[Tuple[IPAddress, int]] = set()
    for server in srvs:
        lhs, sep, rhs = server.rpartition("#")
        if sep:
            srv, port = lhs, int(rhs)
        else:
            srv, port = rhs, 53

        try:
            ip = ip_address(srv)
        except ValueError:
            try:
                addr_infos = getaddrinfo(srv, "domain")
            except Exception as e:
                msg = f"""
                {e}
                {srv}
                """
                print(dedent(msg), file=stderr)
            else:
                if not addr_infos:
                    msg = f"""
                    WARN :: No IPs found for DNS server :: {srv}
                    """
                    print(dedent(msg), file=stderr)
                else:
                    for _, _, _, _, info in addr_infos:
                        addr, *_ = info
                        ip = ip_address(addr)
                        if ip not in seen:
                            pair = ip, port
                            seen.add(pair)
                            yield pair
        else:
            if ip not in seen:
                pair = ip, port
                seen.add(pair)
                yield pair
    else:
        if not seen:
            raise RuntimeError(f"NO DNS SERVERS -- {srvs}")


def _static_dns_records(splits: AbstractSet[Split]) -> Iterator[_DNS_Record]:
    it: Iterable[Tuple[str, AbstractSet[IPAddress]]] = chain(
        ((split.DOMAIN, {split.ADDR.V4, split.ADDR.V6}) for split in splits),
        settings().dns.records.items(),
    )

    for hostname, addresses in it:
        for address in addresses:
            record_type = "A" if isinstance(address, IPv4Address) else "AAAA"
            yield _DNS_Record(
                ADDR=address,
                NAME=hostname,
                TYPE=record_type,
            )


def _env(networks: Networks) -> Mapping[str, Any]:
    fwds, avail, splits = forwarded_ports(networks)
    loop_back = calculate_loopback()
    env = {
        "CPU_COUNT": cpu_count(),
        "DHCP_FIXED": dhcp_fixed(chain(fwds, avail, splits)),
        "DHCP_LEASE_TIME": settings().dhcp.lease_time,
        "DNS_ADDRS": _resolv_addrs(),
        "FORWARDED_PORTS": fwds,
        "GUEST_ACCESSIBLE": avail,
        "GUEST_DOMAIN": settings().dns.local_domains.guest,
        "GUEST_IF": settings().interfaces.guest,
        "GUEST_NETWORK_V4": networks.guest.v4,
        "GUEST_NETWORK_V6": networks.guest.v6,
        "IPV6_ENABLED": ipv6_enabled(),
        "IPV6_PD": settings().ip_addresses.ipv6.prefix_delegation,
        "IPV6_ULA": PRIVATE_V6,
        "LINK_LOCAL_V6": LINK_LOCAL_V6,
        "LOCAL_TTL": settings().dns.local_ttl,
        "LOOPBACK_LOCAL": loop_back,
        "LOOPBACK_V4": LOOPBACK_V4,
        "LOOPBACK_V6": LOOPBACK_V6,
        "PRIVATE_ADDRS": PRIVATE_ADDRS,
        "PRIVATE_DOMAINS": settings().dns.private_domains,
        "SERVER_NAME": SERVER_NAME,
        "SQUID_PORT": settings().port_bindings.squid,
        "STATIC_DNS_RECORDS": _static_dns_records(splits),
        "STATS_PORT": settings().port_bindings.statistics,
        "TOR_NETWORK_V4": networks.tor.v4,
        "TOR_NETWORK_V6": networks.tor.v6,
        "TOR_PORT": settings().port_bindings.tor,
        "TRUSTED_DOMAIN": settings().dns.local_domains.trusted,
        "TRUSTED_IF": settings().interfaces.trusted,
        "TRUSTED_NETWORK_V4": networks.trusted.v4,
        "TRUSTED_NETWORK_V6": networks.trusted.v6,
        "USER": USER,
        "WAN_IF": settings().interfaces.wan,
        "WG": wg_env(networks),
        "WG_DOMAIN": settings().dns.local_domains.wireguard,
        "WG_IF": settings().interfaces.wireguard,
        "WG_NETWORK_V4": networks.wireguard.v4,
        "WG_NETWORK_V6": networks.wireguard.v6,
        "WG_PORT": settings().port_bindings.wireguard,
        "WG_RECORDS": wg_records(networks),
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
                networks.trusted.v4,
                networks.trusted.v6,
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
                f"/CN={SERVER_NAME}.{settings().dns.local_domains.trusted}",
                "-addext",
                f"subjectAltName={','.join(san)}",
            )
        )


def _pprn() -> None:
    cols, _ = get_terminal_size()
    print(
        pformat(
            settings(),
            indent=2,
            width=cols,
        ),
        file=stderr,
    )


def main() -> None:
    _pprn()

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
