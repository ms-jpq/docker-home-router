from dataclasses import dataclass
from ipaddress import IPv6Address
from json import dumps, loads
from subprocess import check_output
from typing import Optional, Sequence

from std2.ipaddress import LINK_LOCAL_V6
from std2.pickle import decode
from std2.pickle.coders import BUILTIN_DECODERS
from std2.types import IPAddress

from .consts import IPV6_STAT, WAN_IF


@dataclass(frozen=True)
class _AddrInfo:
    local: IPAddress
    prefixlen: int


@dataclass(frozen=True)
class Addr:
    ifname: str
    addr_info: Sequence[_AddrInfo]
    address: Optional[str] = None


Addrs = Sequence[Addr]


def addr_show() -> Addrs:
    raw = check_output(("ip", "--json", "address", "show"), text=True)
    json = loads(raw)
    addrs: Addrs = decode(Addrs, json, strict=False, decoders=BUILTIN_DECODERS)
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


def ipv6_enabled() -> bool:
    def cont() -> bool:
        for addr in addr_show():
            if addr.ifname == WAN_IF:
                for info in addr.addr_info:
                    if (
                        isinstance(info.local, IPv6Address)
                        and info.local not in LINK_LOCAL_V6
                    ):
                        return True
        else:
            return False

    if IPV6_STAT.exists():
        val: bool = loads(IPV6_STAT.read_text())
        return val
    else:
        val = cont()
        IPV6_STAT.write_text(dumps(val))
        return val
