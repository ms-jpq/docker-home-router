from json import dumps
from subprocess import check_output
from typing import Sequence, Tuple

from std2.pickle.encoder import new_encoder

from ..consts import SHORT_DURATION
from ..forwards import Available, Forwarded, forwarded_ports
from .subnets import load_networks


def feed() -> str:
    coder = new_encoder[Tuple[Sequence[Forwarded], Sequence[Available]]](
        Tuple[Sequence[Forwarded], Sequence[Available]]
    )
    networks = load_networks()
    f, g = forwarded_ports(networks)
    data = coder((tuple(f), tuple(g)))
    json = dumps(data, check_circular=False, ensure_ascii=False, allow_nan=False)
    raw = check_output(("sortd", "yaml"), text=True, input=json, timeout=SHORT_DURATION)
    return raw.strip()
