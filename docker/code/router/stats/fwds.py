from dataclasses import asdict
from itertools import chain
from json import dumps
from subprocess import check_output

from ..consts import SHORT_DURATION
from ..forwards import forwarded_ports
from .subnets import load_networks


def feed() -> str:
    networks = load_networks()
    raw = forwarded_ports(networks)
    data = tuple({k: str(v) for k, v in asdict(dc)} for dc in chain.from_iterable(raw))
    json = dumps(data, check_circular=False, ensure_ascii=False, allow_nan=False)
    raw = check_output(("sortd", "yaml"), text=True, input=json, timeout=SHORT_DURATION)
    return raw.strip()
