from ipaddress import IPv4Address, ip_interface, ip_network
from re import RegexFlag, compile
from subprocess import check_call
from typing import AbstractSet, MutableSet, Optional

from std2.ipaddress import LINK_LOCAL_V6, IPInterface, IPNetwork

from ..consts import DHCP_CLIENT_LEASES
from ..ifup.main import if_up
from ..ip import Addrs, addr_show, ipv6_enabled
from ..options.parser import settings
from ..subnets import load_networks


def _wan_pd() -> Optional[IPNetwork]:
    try:
        lease = DHCP_CLIENT_LEASES.read_text()
    except FileNotFoundError:
        return None
    else:
        re = compile(
            r"^\s*iaprefix\s+(?P<network>[^s]+)\s+\{$", flags=RegexFlag.MULTILINE
        )

        if match := re.search(lease):
            net = match.group("network")
            try:
                network: IPNetwork = ip_network(net)
            except ValueError:
                return None
            else:
                return network
        else:
            return None


def if_up(addrs: Addrs, interface: str, networks: AbstractSet[IPNetwork]) -> None:
    acc: MutableSet[IPInterface] = {
        ip_interface(f"{next(network.hosts())}/{network.prefixlen}")
        for network in networks
    }

    check_call(("ip", "link", "set", "up", "dev", interface))

    for addr in addrs:
        if addr.ifname == interface:
            for info in addr.addr_info:
                local = ip_interface(f"{info.local}/{info.prefixlen}")
                if info.tentative:
                    check_call(("ip", "addr", "del", str(local), "dev", interface))
                elif local in acc:
                    acc.discard(local)
                else:
                    if local.ip not in LINK_LOCAL_V6:
                        check_call(("ip", "addr", "del", str(local), "dev", interface))
            break
    else:
        raise ValueError(f"IF NOT FOUND - {interface}")

    for ip in acc:
        if isinstance(ip, IPv4Address) or ipv6_enabled():
            check_call(("ip", "addr", "add", str(ip), "dev", interface))


def main() -> None:
    networks = load_networks()
    addrs = addr_show()
    if network := _wan_pd():
        if_up(
            addrs,
            interface=settings().interfaces.wan,
            networks={network},
        )

    if_up(
        addrs,
        interface=settings().interfaces.trusted,
        networks={networks.trusted.v4, networks.trusted.v6},
    )

    if guest_if := settings().interfaces.guest:
        if_up(
            addrs,
            interface=guest_if,
            networks={networks.guest.v4, networks.guest.v6},
        )
