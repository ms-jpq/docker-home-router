from ..ip import ipv6_enabled
from ..options.parser import settings


def main() -> None:
    if settings().interfaces.wan_pd_only and ipv6_enabled():
        pass
