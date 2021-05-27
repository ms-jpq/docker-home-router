from ..consts import LEASES


def feed() -> str:
    LEASES.parent.mkdir(parents=True, exist_ok=True)
    LEASES.touch()
    leases = LEASES.read_text()
    return leases.strip()
