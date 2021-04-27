from os import linesep

from ..consts import ADDN_HOSTS, DYN, LEASES


def feed() -> str:
    for path in (ADDN_HOSTS, DYN, LEASES):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()

    addns, dyn, leases = ADDN_HOSTS.read_text(), DYN.read_text(), LEASES.read_text()
    return addns.strip() + linesep * 3 + dyn.strip() + linesep * 3 + leases.strip()
