from os import linesep

from ..consts import DYN, LEASES


def feed() -> str:
    DYN.parent.mkdir(parents=True, exist_ok=True)
    LEASES.parent.mkdir(parents=True, exist_ok=True)
    DYN.touch()
    LEASES.touch()

    dyn, leases = DYN.read_text(), LEASES.read_text()
    return dyn + linesep * 3 + leases
