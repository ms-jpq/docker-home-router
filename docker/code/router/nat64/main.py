from subprocess import check_call

from ..consts import RUN
from ..ifup.main import if_up
from ..ip import addr_show
from ..options.parser import settings
from ..subnets import load_networks


def main() -> None:
    try:
        networks = load_networks()
        addrs = addr_show()
        check_call(("tayga", "--config", RUN / "tayga" / "0-main.conf", "--mktun"))
        if_up(
            addrs,
            delete=True,
            interfaces=(settings().interfaces.nat64_if,),
            networks={networks.nat64.v4, networks.nat64.v6},
        )

    except Exception as e:
        print(e, flush=True)
        pass
