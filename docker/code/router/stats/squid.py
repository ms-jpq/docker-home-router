from subprocess import check_output

from ..consts import SHORT_DURATION
from ..subnets import calculate_loopback


def feed() -> str:
    loopback = calculate_loopback()
    raw = check_output(
        ("squidclient", "--host", str(loopback), "mgr:utilization"),
        text=True,
        timeout=SHORT_DURATION,
    )
    return raw.strip()
