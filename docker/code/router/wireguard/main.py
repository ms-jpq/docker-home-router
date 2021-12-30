from subprocess import check_call

from ..consts import RUN
from ..ifup.main import if_up
from ..ip import addr_show, link_show
from ..options.parser import settings
from ..subnets import load_networks

_SRV_CONF = RUN / "wireguard" / "server.conf"


def _add_link() -> None:
    for link in link_show():
        if link.ifname == settings().interfaces.wan:
            break
    else:
        check_call(
            ("ip", "link", "add", settings().interfaces.wan, "type", "wireguard")
        )


def _set_up() -> None:
    check_call(
        (
            "ip",
            "link",
            "set",
            "multicast",
            "on",
            "dev",
            settings().interfaces.wan,
        )
    )
    check_call(
        (
            "ip",
            "link",
            "set",
            "up",
            "dev",
            settings().interfaces.wan,
        )
    )


def _wg_up() -> None:
    check_call(
        (
            "wg",
            "setconf",
            settings().interfaces.wan,
            _SRV_CONF,
        )
    )


def main() -> None:
    networks = load_networks()
    addrs = addr_show()
    _add_link()
    if_up(
        addrs,
        interface=settings().interfaces.wan,
        networks={networks.wireguard.v4, networks.wireguard.v6},
    )
    _wg_up()
    _set_up()
