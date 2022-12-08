from subprocess import check_call, run

from ..consts import RUN, TUNNABLE
from ..options.parser import settings
from ..subnets import load_networks


def main() -> None:
    if TUNNABLE:
        pass
