from ipaddress import ip_interface
from subprocess import check_call
from typing import AbstractSet, MutableSet

from std2.types import IPInterface, IPNetwork

from ..consts import GUEST_IF, LAN_IF
from ..ip import Addrs, addr_show
from ..subnets import load_networks


def if_up(addrs: Addrs, interface: str, networks: AbstractSet[IPNetwork]) -> None:
    acc: MutableSet[IPInterface] = {
        ip_interface(f"{next(network.hosts())}/{network.prefixlen}")
        for network in networks
    }

    for addr in addrs:
        if addr.ifname == interface:
            for info in addr.addr_info:
                local: IPInterface = ip_interface(f"{info.local}/{info.prefixlen}")
                if local in acc:
                    acc.discard(local)
                else:
                    check_call(("ip", "addr", "del", str(local), "dev", interface))
            break
    else:
        raise ValueError(f"IF NOT FOUND - {interface}")

    for ip in acc:
        check_call(("ip", "addr", "add", str(ip), "dev", interface))


def main() -> None:
    networks = load_networks()
    addrs = addr_show()
    if_up(
        addrs,
        interface=LAN_IF,
        networks={networks.lan.v4, networks.lan.v6},
    )

    if GUEST_IF:
        if_up(
            addrs,
            interface=GUEST_IF,
            networks={networks.guest.v4, networks.guest.v6},
        )
