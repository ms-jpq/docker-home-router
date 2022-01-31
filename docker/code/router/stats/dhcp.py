from ..consts import DHCP_SERVER_LEASES


def feed() -> str:
    DHCP_SERVER_LEASES.parent.mkdir(parents=True, exist_ok=True)
    DHCP_SERVER_LEASES.touch()
    leases = DHCP_SERVER_LEASES.read_text()
    return leases.strip()
