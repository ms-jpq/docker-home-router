from subprocess import check_call
from time import sleep

from ..consts import SHORT_DURATION
from ..ip import ipv6_enabled
from ..options.parser import settings


def main() -> None:
    if settings().interfaces.wan_pd_only and ipv6_enabled():
        check_call(("dhclient", "-d", "-6", "-P", settings().interfaces.wan))
    else:
        while True:
            sleep(SHORT_DURATION)
