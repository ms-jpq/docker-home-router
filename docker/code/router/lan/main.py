from os import sep
from pathlib import Path
from subprocess import check_call
from time import sleep

from jinja2 import Environment

from ..consts import J2, LAN_DOMAIN, SHORT_DURATION
from ..records import dns_records
from ..render import j2_build, j2_render

_BASE = Path(sep, "srv", "run", "unbound", "lan")
_DYN = Path("dns", "2-records.conf")
_CONF = _BASE / "1-main.conf"
_RECORDS = _BASE / "2-records.conf"


def _poll(j2: Environment) -> None:
    existing = _RECORDS.read_text()

    env = {
        "DNS_RECORDS": dns_records(),
        "LAN_DOMAIN": LAN_DOMAIN,
    }
    new = j2_render(j2, path=_DYN, env=env)
    if new != existing:
        check_call(
            ("unbound-control", "-c", str(_CONF), "reload"), timeout=SHORT_DURATION
        )


def main() -> None:
    j2 = j2_build(J2)
    while True:
        _poll(j2)
        sleep(SHORT_DURATION)
