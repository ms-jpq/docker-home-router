from dataclasses import dataclass
from fnmatch import fnmatch
from hashlib import sha256
from ipaddress import IPv4Address, IPv4Network, IPv6Network, ip_interface
from itertools import chain, islice
from json import loads
from typing import Iterable, Iterator, Optional, Sequence

from std2.ipaddress import PRIVATE_V4, LOOPBACK_V4
from std2.pickle import decode
from std2.pickle.coders import BUILTIN_DECODERS
from std2.types import IPInterface

from .consts import (
    IF_EXCLUSIONS,
    IP4_EXCLUSION,
    IP4_PREFIX,
    IP6_ULA_GLOBAL,
    IP6_ULA_SUBNET_EXCLUSION,
    LOOPBACK_EXCLUSION,
    NETWORKS_JSON,
    TOR_IP4_PREFIX,
    WAN_IF,
)
from .ip import addr_show
from .types import DualStack, Networks



@dataclass(frozen=True)
class _V4Stack:
    lan: IPv4Network
    wg: IPv4Network
    tor: IPv4Network
    guest: IPv4Network


@dataclass(frozen=True)
class _V6Stack:
    lan: IPv6Network
    wg: IPv6Network
    tor: IPv6Network
    guest: IPv6Network


def load_networks() -> Networks:
    json = loads(NETWORKS_JSON.read_text())
    networks: Networks = decode(Networks, json, decoders=BUILTIN_DECODERS)
    return networks


def _private_subnets(prefix: int) -> Iterator[IPv4Network]:
    for network in PRIVATE_V4:
        for subnet in network.subnets(new_prefix=prefix):
            yield subnet


def _existing(patterns: Sequence[str]) -> Iterator[IPv4Network]:
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


def _v4(if_exclusions: Sequence[str], exclusions: Sequence[IPv4Network]) -> _V4Stack:
    nono = chain(exclusions, _existing(if_exclusions))
    lan, wg, tor, guest = _pick_private(
        nono, prefixes=(IP4_PREFIX, IP4_PREFIX, TOR_IP4_PREFIX, IP4_PREFIX)
    )
    stack = _V4Stack(lan=lan, wg=wg, tor=tor, guest=guest)
    return stack


def _gen_prefix() -> str:
    for addr in addr_show():
        if addr.ifname == WAN_IF:
            if addr.address:
                hashed = int(sha256(addr.address.encode()).hexdigest(), 16)
                integer = hashed % (2 ** 40 - 1)
                bits = format(integer, "08x")
                prefix = f"fd{bits[:2]}:{bits[2:6]}:{bits[6:]}"
                return prefix
    else:
        raise ValueError()


def _v6(prefix: Optional[str], subnets: Sequence[str]) -> _V6Stack:
    org_prefix = prefix or _gen_prefix()
    org = IPv6Network(f"{org_prefix}::/48")
    seen = {IPv6Network(f"{org_prefix}:{subnet}::/64") for subnet in subnets}
    lan, wg, tor, guest = islice(
        (subnet for subnet in org.subnets(new_prefix=64) if subnet not in seen), 4
    )

    stack = _V6Stack(lan=lan, wg=wg, tor=tor, guest=guest)
    return stack


def calculate_networks() -> Networks:
    patterns = (WAN_IF, *IF_EXCLUSIONS)
    v4, v6 = _v4(patterns, exclusions=IP4_EXCLUSION), _v6(
        IP6_ULA_GLOBAL, IP6_ULA_SUBNET_EXCLUSION
    )
    networks = Networks(
        lan=DualStack(v4=v4.lan, v6=v6.lan),
        wireguard=DualStack(v4=v4.wg, v6=v6.wg),
        tor=DualStack(v4=v4.tor, v6=v6.tor),
        guest=DualStack(v4=v4.guest, v6=v6.guest),
    )
    return networks


def calculate_loopback() -> IPv4Address:
    for ip in LOOPBACK_V4.hosts():
        if all(ip not in network for network in LOOPBACK_EXCLUSION):
            return ip
    else:
        raise ValueError()
