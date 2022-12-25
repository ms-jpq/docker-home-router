from dataclasses import dataclass
from functools import lru_cache
from ipaddress import IPv6Address
from json import dumps, loads
from subprocess import check_output
from typing import AbstractSet, Optional, Sequence

from std2.ipaddress import IPAddress
from std2.pickle.decoder import new_decoder

from .consts import IPV6_JSON
from .options.parser import settings


@dataclass(frozen=True)
class _AddrInfo:
    local: IPAddress
    prefixlen: int
    tentative: bool = False


@dataclass(frozen=True)
class Addr:
    ifname: str
    addr_info: Sequence[_AddrInfo]
    address: Optional[str] = None


Addrs = Sequence[Addr]


def addr_show() -> Addrs:
    raw = check_output(("ip", "--json", "address", "show"), text=True)
    json = loads(raw)
    addrs = new_decoder[Addrs](Addrs, strict=False)(json)
    return addrs


def link_show(type: str) -> AbstractSet[str]:
    raw = check_output(("ip", "--json", "link", "show", "type", type))
    json = loads(raw)
    ifaces: AbstractSet[str] = {iface for link in json if (iface := link.get("ifname"))}
    return ifaces


@dataclass(frozen=True)
class Link:
    ifname: str


@lru_cache(maxsize=None)
def ipv6_enabled() -> bool:
    def cont() -> bool:
        for addr in addr_show():
            if addr.ifname == settings().interfaces.wan:
                for info in addr.addr_info:
                    if isinstance(info.local, IPv6Address):
                        return True
        else:
            return False

    if IPV6_JSON.exists():
        val: bool = loads(IPV6_JSON.read_text())
        return val
    else:
        val = cont()
        IPV6_JSON.write_text(dumps(val))
        return val
