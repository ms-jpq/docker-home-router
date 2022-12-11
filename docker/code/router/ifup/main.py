from ipaddress import IPv4Address, ip_interface
from locale import strxfrm
from subprocess import check_call
from typing import AbstractSet, Iterable, MutableSet

from std2.ipaddress import LINK_LOCAL_V6, IPInterface, IPNetwork

from ..ip import Addrs, addr_show, ipv6_enabled
from ..options.parser import settings
from ..subnets import load_networks


def if_up(
    addrs: Addrs,
    keep_tentative: bool,
    interfaces: Iterable[str],
    networks: AbstractSet[IPNetwork],
) -> None:

    for idx, interface in enumerate(sorted(interfaces, key=strxfrm), start=1):
        acc: MutableSet[IPInterface] = {
            ip_interface(f"{network[idx]}/{network.prefixlen}") for network in networks
        }
        check_call(("ip", "link", "set", "up", "dev", interface))

        for addr in addrs:
            if addr.ifname == interface:
                for info in addr.addr_info:
                    local = ip_interface(f"{info.local}/{info.prefixlen}")
                    if not keep_tentative and info.tentative:
                        check_call(("ip", "addr", "del", str(local), "dev", interface))
                    elif local in acc:
                        acc.discard(local)
                    else:
                        if local.ip not in LINK_LOCAL_V6:
                            check_call(
                                ("ip", "addr", "del", str(local), "dev", interface)
                            )
                break
        else:
            raise ValueError(f"IF NOT FOUND - {interface}")

        for ip in acc:
            if isinstance(ip, IPv4Address) or ipv6_enabled():
                check_call(("ip", "addr", "replace", str(ip), "dev", interface))


def main() -> None:
    networks = load_networks()
    addrs = addr_show()

    if_up(
        addrs,
        keep_tentative=False,
        interfaces=settings().interfaces.trusted,
        networks={networks.trusted.v4, networks.trusted.v6},
    )

    if guest_if := settings().interfaces.guest:
        if_up(
            addrs,
            keep_tentative=False,
            interfaces=guest_if,
            networks={networks.guest.v4, networks.guest.v6},
        )
