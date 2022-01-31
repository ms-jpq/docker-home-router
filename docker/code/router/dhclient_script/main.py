from ipaddress import ip_network
from re import RegexFlag, compile
from typing import Optional

from std2.ipaddress import IPNetwork

from ..consts import DHCP_CLIENT_LEASES
from ..ifup.main import if_up
from ..ip import addr_show, ipv6_enabled
from ..options.parser import settings


def _parse(lease: str) -> Optional[IPNetwork]:
    re = compile(r"^\s*iaprefix\s+(?P<network>[^s]+)\s+\{$", flags=RegexFlag.MULTILINE)

    if match := re.search(lease):
        net = match.group("network")
        try:
            network: IPNetwork = ip_network(net)
        except ValueError:
            return None
        else:
            return network
    return None


def main() -> None:
    if settings().interfaces.wan_pd_only and ipv6_enabled():
        try:
            lease = DHCP_CLIENT_LEASES.read_text()
        except FileNotFoundError:
            pass
        else:
            if network := _parse(lease):
                addrs = addr_show()
                if_up(
                    addrs,
                    interface=settings().interfaces.wan,
                    networks={network},
                )
