from subprocess import check_call, run

from ..consts import RUN, TUNNABLE
from ..options.parser import settings
from ..subnets import load_networks


def main() -> None:
    if TUNNABLE:
        if_name = settings().interfaces.nat64_if
        networks = load_networks()
        main_if = networks.nat64 if settings().interfaces.guest else networks.trusted

        run(("ip", "link", "del", "dev", if_name))
        check_call(("tayga", "--config", RUN / "tayga" / "0-main.conf", "--mktun"))

        check_call(("ip", "link", "set", "dev", if_name, "up"))
        check_call(("ip", "addr", "add", str(next(main_if.v6.hosts())), "dev", if_name))
        check_call(("ip", "addr", "add", str(next(main_if.v4.hosts())), "dev", if_name))
        check_call(("ip", "route", "add", str(networks.nat64.v4), "dev", if_name))
        check_call(("ip", "route", "add", str(networks.nat64.v6), "dev", if_name))
