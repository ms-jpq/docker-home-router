from subprocess import check_call, run

from ..consts import RUN
from ..options.parser import settings
from ..subnets import load_networks


def main() -> None:
    if_name = settings().interfaces.nat64_if
    networks = load_networks()
    main_if = networks.nat64 if settings().interfaces.guest else networks.trusted
    try:
        run(("ip", "link", "del", "dev", if_name))
        check_call(("tayga", "--config", RUN / "tayga" / "0-main.conf", "--mktun"))

        check_call(("ip", "addr", "add", str(next(main_if.v6.hosts())), "dev", if_name))
        check_call(("ip", "addr", "add", str(next(main_if.v4.hosts())), "dev", if_name))
        check_call(("ip", "route", "add", str(networks.nat64.v4), "dev", if_name))
        check_call(("ip", "route", "add", str(networks.nat64.v6), "dev", if_name))

    except Exception as e:
        print(e, flush=True)
        pass
