from subprocess import call, check_call
from time import sleep

from ..consts import DHCP_CLIENT_LEASES, SHORT_DURATION
from ..ip import ipv6_enabled
from ..options.parser import settings


def main() -> None:
    DHCP_CLIENT_LEASES.parent.mkdir(parents=True, exist_ok=True)
    if settings().interfaces.wan_pd_only and ipv6_enabled():
        code = call(
            (
                "dhclient",
                "-d",
                "--no-pid",
                "-lf",
                DHCP_CLIENT_LEASES,
                "-6",
                "-P",
                settings().interfaces.wan,
            )
        )
        print("DHCP - client --> ", code)
    else:
        while True:
            sleep(SHORT_DURATION)
