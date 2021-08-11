from subprocess import check_call

from ..consts import RUN, WG_IF
from ..ifup.main import if_up
from ..ip import addr_show, link_show
from ..subnets import load_networks

_SRV_CONF = RUN / "wireguard" / "server.conf"


def _add_link() -> None:
    for link in link_show():
        if link.ifname == WG_IF:
            break
    else:
        check_call(("ip", "link", "add", WG_IF, "type", "wireguard"))


def _set_up() -> None:
    check_call(("ip", "link", "set", "multicast", "on", "dev", WG_IF))
    check_call(("ip", "link", "set", "up", "dev", WG_IF))


def _wg_up() -> None:
    check_call(("wg", "setconf", WG_IF, _SRV_CONF))


def main() -> None:
    networks = load_networks()
    addrs = addr_show()
    _add_link()
    if_up(
        addrs, interface=WG_IF, networks={networks.wireguard.v4, networks.wireguard.v6}
    )
    _wg_up()
    _set_up()
