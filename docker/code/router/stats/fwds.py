from json import dumps
from subprocess import check_output
from typing import AbstractSet, Tuple

from std2.pickle.encoder import new_encoder

from ..consts import SHORT_DURATION
from ..forwards import Available, Forwarded, forwarded_ports
from .subnets import load_networks


def feed() -> str:
    coder = new_encoder[Tuple[AbstractSet[Forwarded], AbstractSet[Available]]](
        Tuple[AbstractSet[Forwarded], AbstractSet[Available]]
    )
    networks = load_networks()
    data = coder(forwarded_ports(networks))
    json = dumps(data, check_circular=False, ensure_ascii=False, allow_nan=False)
    raw = check_output(("sortd", "yaml"), text=True, input=json, timeout=SHORT_DURATION)
    return raw.strip()
