from subprocess import check_call, run

from ..consts import RUN, TUNNABLE
from ..options.parser import settings
from ..subnets import load_networks


def main() -> None:
    if TUNNABLE:
        if_name = settings().interfaces.nat64_if
        networks = load_networks()
        ipv6 = str(next(networks.nat64.v6.hosts()))

        run(("ip", "link", "del", "dev", if_name))
        check_call(("tayga", "--config", RUN / "tayga" / "0-main.conf", "--mktun"))

        check_call(("ip", "link", "set", "dev", if_name, "up"))

        check_call(("ip", "addr", "add", ipv6, "dev", if_name))

        check_call(("ip", "route", "add", str(networks.nat64.v4), "dev", if_name))
        check_call(("ip", "-6", "route", "add", str(networks.nat64.v6), "dev", if_name))
