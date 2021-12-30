from dataclasses import dataclass
from fnmatch import fnmatch
from hashlib import sha256
from ipaddress import IPv4Address, IPv4Network, IPv6Network, ip_interface
from itertools import chain, islice
from json import loads
from typing import AbstractSet, Iterable, Iterator, Optional

from std2.ipaddress import LOOPBACK_V4, PRIVATE_V4, IPInterface
from std2.pickle.decoder import new_decoder

from .consts import NETWORKS_JSON
from .ip import addr_show
from .options.parser import settings
from .types import DualStack, Networks


@dataclass(frozen=True)
class _V4Stack:
    trusted: IPv4Network
    wg: IPv4Network
    tor: IPv4Network
    guest: IPv4Network


@dataclass(frozen=True)
class _V6Stack:
    trusted: IPv6Network
    wg: IPv6Network
    tor: IPv6Network
    guest: IPv6Network


def load_networks() -> Networks:
    json = loads(NETWORKS_JSON.read_text())
    networks = new_decoder[Networks](Networks)(json)
    return networks


def _private_subnets(prefix: int) -> Iterator[IPv4Network]:
    for network in PRIVATE_V4:
        for subnet in network.subnets(new_prefix=max(network.prefixlen, prefix)):
            yield subnet


def _existing(patterns: AbstractSet[str]) -> Iterator[IPv4Network]:
    for addr in addr_show():
        if any(fnmatch(addr.ifname, pat=pattern) for pattern in patterns):
            for info in addr.addr_info:
                net: IPInterface = ip_interface(f"{info.local}/{info.prefixlen}")
                if isinstance(net.network, IPv4Network):
                    yield net.network


def _pick_private(
    existing: Iterable[IPv4Network], prefixes: Iterable[int]
) -> Iterator[IPv4Network]:
    seen = {*existing}

    for prefix in prefixes:
        for candidate in _private_subnets(prefix):
            if all(
                not candidate.overlaps(network) and not network.overlaps(candidate)
                for network in seen
            ):
                seen.add(candidate)
                yield candidate
                break
        else:
            raise RuntimeError(f"No network available -- prefix :: {prefix}")


def _v4(
    if_exclusions: AbstractSet[str], exclusions: AbstractSet[IPv4Network]
) -> _V4Stack:
    nono = chain(exclusions, _existing(if_exclusions))
    trusted, wg, tor, guest = _pick_private(
        nono,
        prefixes=(
            settings().ip_addresses.ipv4.managed_prefix_len,
            settings().ip_addresses.ipv4.managed_prefix_len,
            settings().ip_addresses.ipv4.tor_prefix_len,
            settings().ip_addresses.ipv4.managed_prefix_len,
        ),
    )
    stack = _V4Stack(trusted=trusted, wg=wg, tor=tor, guest=guest)
    return stack


def _gen_prefix() -> str:
    for addr in addr_show():
        if addr.ifname == settings().interfaces.wan:
            if addr.address:
                hashed = int(sha256(addr.address.encode()).hexdigest(), 16)
                integer = hashed % (2 ** 40 - 1)
                bits = format(integer, "08x")
                prefix = f"fd{bits[:2]}:{bits[2:6]}:{bits[6:]}"
                return prefix
    else:
        raise ValueError()


def _v6(prefix: Optional[str]) -> _V6Stack:
    org_prefix = prefix or _gen_prefix()
    org = IPv6Network(f"{org_prefix}::/48")
    trusted, wg, tor, guest = islice(org.subnets(new_prefix=64), 4)

    stack = _V6Stack(trusted=trusted, wg=wg, tor=tor, guest=guest)
    return stack


def calculate_networks() -> Networks:
    patterns = {settings().interfaces.wan, *settings().interfaces.unmanaged}
    v4 = _v4(
        patterns,
        exclusions=settings().ip_addresses.ipv4.managed_network_exclusions,
    )
    v6 = _v6(settings().ip_addresses.ipv6.ula_global_prefix)

    networks = Networks(
        trusted=DualStack(v4=v4.trusted, v6=v6.trusted),
        wireguard=DualStack(v4=v4.wg, v6=v6.wg),
        tor=DualStack(v4=v4.tor, v6=v6.tor),
        guest=DualStack(v4=v4.guest, v6=v6.guest),
    )
    return networks


def calculate_loopback() -> IPv4Address:
    for ip in LOOPBACK_V4.hosts():
        if all(
            ip not in network
            for network in settings().ip_addresses.ipv4.loopback_exclusions
        ):
            return ip
    else:
        raise ValueError()
