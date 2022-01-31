from subprocess import check_call
from time import sleep

from ..consts import DHCP_CLIENT_LEASES, RUN, SHORT_DURATION
from ..ip import ipv6_enabled
from ..options.parser import settings


def main() -> None:
    if settings().interfaces.wan_pd_only and ipv6_enabled():
        check_call(
            (
                "dhclient",
                "-d",
                "--no-pid",
                "-lf",
                DHCP_CLIENT_LEASES,
                "-sf",
                RUN / "dhclient/ctl.sh",
                "-6",
                "-P",
                settings().interfaces.wan,
            )
        )
    else:
        while True:
            sleep(SHORT_DURATION)
