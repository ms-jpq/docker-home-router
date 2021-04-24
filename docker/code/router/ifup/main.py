from subprocess import check_call
from typing import AbstractSet

from std2.types import IPAddress

from ..consts import GUEST_IF, LAN_IF
from ..ip import Addrs, addr_show
from ..subnets import load_networks


def _if_up(addrs: Addrs, interface: str, ips: AbstractSet[IPAddress]) -> None:
    acc = {*ips}

    for addr in addrs:
        if addr.ifname == interface:
            for info in addr.addr_info:
                acc.discard(info.local)
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
        ips={next(networks.lan.v4.hosts()), next(networks.lan.v6.hosts())},
    )

    if GUEST_IF:
        _if_up(
            addrs,
            interface=GUEST_IF,
            ips={next(networks.guest.v4.hosts()), next(networks.guest.v6.hosts())},
        )
