from os import sep
from pathlib import Path, PurePath
from subprocess import check_call
from time import sleep

from jinja2 import Environment

from ..consts import LAN_DOMAIN, LOCAL_TTL, RUN, SHORT_DURATION
from ..records import dns_records
from ..render import j2_build, j2_render
from ..subnets import load_networks

_BASE = RUN / "unbound" / "lan"
_J2 = Path(sep, "srv", "templates", "unbound", "lan", "conf.d")
_DYN = PurePath("2-records.conf")
_CONF = _BASE / "1-main.conf"
_RECORDS = _BASE / "conf.d" / "2-records.conf"


def _poll(j2: Environment) -> None:
    existing = _RECORDS.read_text()
    networks = load_networks()

    env = {
        "LAN_DOMAIN": LAN_DOMAIN,
        "LOCAL_TTL": LOCAL_TTL,
        "DNS_RECORDS": dns_records(networks),
    }
    new = j2_render(j2, path=_DYN, env=env)
    if new != existing:
        _RECORDS.write_text(new)
        check_call(
            ("unbound-control", "-c", str(_CONF), "reload"), timeout=SHORT_DURATION
        )


def main() -> None:
    j2 = j2_build(_J2)
    while True:
        _poll(j2)
        sleep(SHORT_DURATION)
