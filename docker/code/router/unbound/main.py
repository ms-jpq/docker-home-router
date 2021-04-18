from json import dumps
from subprocess import check_output
from typing import Any, Tuple, Union

from std2.configparser import hydrate

from ..consts import TIMEOUT
from ..show import show

_TITLE = "UNBOUND"


def _parse_stat(line: str) -> Tuple[str, Union[int, float]]:
    key, _, val = line.partition("=")
    try:
        return key, int(val)
    except ValueError:
        return key, float(val)


def _parse_stats(raw: str) -> Any:
    data = {
        key: val
        for key, val in (_parse_stat(line) for line in raw.splitlines() if line)
    }
    stat = hydrate(data)
    return stat


def _feed() -> str:
    raw = check_output(("unbound-control", "stats_noreset"), text=True, timeout=TIMEOUT)
    data = _parse_stats(raw)
    json = dumps(
        data,
        check_circular=False,
        ensure_ascii=False,
    )
    yaml = check_output(("sortd", "yaml"), text=True, input=json)
    return yaml


def main() -> None:
    show(_TITLE, port=60692, feed=_feed)
