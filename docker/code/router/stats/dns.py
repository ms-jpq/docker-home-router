from json import dumps
from subprocess import check_output
from typing import Any, Tuple, Union

from std2.configparser import hydrate

from ..consts import RUN, SHORT_DURATION

_CONF = RUN / "unbound" / "main" / "1-main.conf"


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


def feed() -> str:
    raw = check_output(
        ("unbound-control", "-c", str(_CONF), "stats_noreset"),
        text=True,
        timeout=SHORT_DURATION,
    )
    data = _parse_stats(raw)
    json = dumps(data, check_circular=False, ensure_ascii=False)
    yaml = check_output(("sortd", "yaml"), text=True, input=json)
    return yaml.strip()
