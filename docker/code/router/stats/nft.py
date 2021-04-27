from subprocess import check_output

from ..consts import TIMEOUT


def feed() -> str:
    raw = check_output(("nft", "list", "ruleset"), text=True, timeout=TIMEOUT)
    return raw.strip()
