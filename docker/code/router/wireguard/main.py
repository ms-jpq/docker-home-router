from subprocess import check_call

from ..consts import RUN
from ..ifup.main import if_up
from ..ip import addr_show, link_show
from ..options.parser import settings
from ..subnets import load_networks

_SRV_CONF = RUN / "wireguard" / "server.conf"


def _add_link() -> None:
    if settings().interfaces.wireguard not in link_show("wireguard"):
        check_call(
            (
                "ip",
                "link",
                "replace",
                settings().interfaces.wireguard,
                "type",
                "wireguard",
            )
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
            settings().interfaces.wireguard,
        )
    )
    check_call(
        (
            "ip",
            "link",
            "set",
            "up",
            "dev",
            settings().interfaces.wireguard,
        )
    )


def _wg_up() -> None:
    check_call(
        (
            "wg",
            "setconf",
            settings().interfaces.wireguard,
            _SRV_CONF,
        )
    )


def main() -> None:
    networks = load_networks()
    addrs = addr_show()
    _add_link()
    if_up(
        addrs,
        keep_tentative=False,
        interfaces=(settings().interfaces.wireguard,),
        networks={networks.wireguard.v4, networks.wireguard.v6},
    )
    _wg_up()
    _set_up()
