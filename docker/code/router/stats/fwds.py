from subprocess import check_output

from std2.tree import recur_sort

from ..consts import TIMEOUT
from ..port_fwd import forwarded_ports


def feed() -> str:
    fwds = forwarded_ports()
    data = recur_sort(fwds)
    raw = check_output(("sortd", "yaml"), text=True, input=data, timeout=TIMEOUT)
    return raw.strip()
