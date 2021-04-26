from ipaddress import ip_interface
from subprocess import check_call
from typing import AbstractSet

from std2.types import IPInterface, IPNetwork

from ..consts import GUEST_IF, LAN_IF
from ..ip import Addrs, addr_show
from ..subnets import load_networks


def _if_up(addrs: Addrs, interface: str, networks: AbstractSet[IPNetwork]) -> None:
    acc: AbstractSet[IPInterface] = {
        ip_interface(f"{next(network.hosts())}/{network.prefixlen}")
        for network in networks
    }

    for addr in addrs:
        if addr.ifname == interface:
            for info in addr.addr_info:
                local: IPInterface = ip_interface(f"{info.local}/{info.prefixlen}")
                acc.discard(local)
            break
    else:
        raise ValueError(f"IF NOT FOUND - {interface}")

    for ip in acc:
        check_call(("ip", "addr", "add", str(ip), "dev", interface))


def main() -> None:
    networks = load_networks()
    addrs = addr_show()
    _if_up(
        addrs,
        interface=LAN_IF,
        networks={networks.lan.v4, networks.lan.v6},
    )

    if GUEST_IF:
        _if_up(
            addrs,
            interface=GUEST_IF,
            networks={networks.guest.v4, networks.guest.v6},
        )
