from ipaddress import IPv4Address, ip_interface
from json import loads
from locale import strxfrm
from subprocess import check_call, check_output
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
                    link_local = local.ip in LINK_LOCAL_V6
                    if not link_local and info.tentative and not keep_tentative:
                        check_call(("ip", "addr", "del", str(local), "dev", interface))
                    elif local in acc:
                        acc.discard(local)
                    else:
                        if not link_local:
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
    interfaces = settings().interfaces
    networks = load_networks()
    addrs = addr_show()

    raw = check_output(("ip", "--json", "link", "show", "type", "bridge"))
    br_names = {bridge["ifname"] for bridge in loads(raw)}

    for bridge in (interfaces.trusted_bridge, interfaces.guest_bridge):
        if bridge not in br_names:
            check_call(("ip", "link", "add", "name", bridge, "type", "bridge"))
            check_call(("ip", "link", "set", "up", "dev", bridge))

    if_up(
        addrs,
        keep_tentative=False,
        interfaces={interfaces.trusted_bridge},
        networks={networks.trusted.v4, networks.trusted.v6},
    )

    if_up(
        addrs,
        keep_tentative=False,
        interfaces={interfaces.guest_bridge},
        networks={networks.trusted.v4, networks.trusted.v6},
    )
