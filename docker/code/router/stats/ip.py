from itertools import chain
from os import linesep
from subprocess import check_output

from ..options.parser import settings


def _show(interface: str) -> str:
    return check_output(("ip", "addr", "show", "dev", interface), text=True)


def feed() -> str:
    interfaces = settings().interfaces
    ifs = chain(
        (interfaces.wireguard, interfaces.trusted_bridge, interfaces.guest_bridge),
        interfaces.trusted,
        interfaces.guest,
        (interfaces.wan,),
    )
    return linesep.join(map(_show, ifs))
