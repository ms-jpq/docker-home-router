from json import dumps
from subprocess import check_output
from typing import Sequence

from std2.pickle.encoder import new_encoder

from ..consts import SHORT_DURATION
from ..port_fwd import Forwarded, forwarded_ports
from .subnets import load_networks


def feed() -> str:
    coder = new_encoder[Sequence[Forwarded]](Sequence[Forwarded])
    networks = load_networks()
    data = coder(tuple(forwarded_ports(networks)))
    json = dumps(data, check_circular=False, ensure_ascii=False, allow_nan=False)
    raw = check_output(("sortd", "yaml"), text=True, input=json, timeout=SHORT_DURATION)
    return raw.strip()
