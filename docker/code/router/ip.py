from dataclasses import dataclass
from json import loads
from subprocess import check_output
from typing import Sequence

from std2.pickle import decode
from std2.pickle.coders import ipv4_addr_decoder, ipv6_addr_decoder
from std2.types import IPAddress


def ipv6_enabled() -> bool:
    raw = check_output(("sysctl", "net.ipv6.conf.all.disable_ipv6"), text=True).rstrip()
    _, _, val = raw.partition(" = ")
    return not int(val)


@dataclass(frozen=True)
class _AddrInfo:
    local: IPAddress
    prefixlen: int


@dataclass(frozen=True)
class Addr:
    addr_info: Sequence[_AddrInfo]


Addrs = Sequence[Addr]


def addr_show() -> Addrs:
    raw = check_output(("ip", "--json", "address", "show"), text=True)
    json = loads(raw)
    addrs: Addrs = decode(
        Addrs, json, strict=False, decoders=(ipv4_addr_decoder, ipv6_addr_decoder)
    )
    return addrs


@dataclass(frozen=True)
class Link:
    ifname: str


Links = Sequence[Link]


def link_show() -> Links:
    raw = check_output(("ip", "--json", "link", "show"), text=True)
    json = loads(raw)
    links: Links = decode(Links, json, strict=False)
    return links
