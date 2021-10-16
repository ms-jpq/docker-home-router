from json import dumps
from subprocess import check_output
from typing import Any, Mapping, Sequence

from std2.pickle.encoder import new_encoder

from ..consts import SHORT_DURATION
from ..port_fwd import forwarded_ports
from .subnets import load_networks


def feed() -> str:
    networks = load_networks()
    tp = Sequence[Mapping[str, Any]]
    data = new_encoder[tp](tp)(tuple(forwarded_ports(networks)))
    json = dumps(data, check_circular=False, ensure_ascii=False)
    raw = check_output(("sortd", "yaml"), text=True, input=json, timeout=SHORT_DURATION)
    return raw.strip()
