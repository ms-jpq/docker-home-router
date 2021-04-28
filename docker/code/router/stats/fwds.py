from json import dumps
from subprocess import check_output

from ..consts import TIMEOUT
from ..port_fwd import forwarded_ports


def feed() -> str:
    data = forwarded_ports()
    json = dumps(data, check_circular=False, ensure_ascii=False)
    raw = check_output(("sortd", "yaml"), text=True, input=json, timeout=TIMEOUT)
    return raw.strip()
