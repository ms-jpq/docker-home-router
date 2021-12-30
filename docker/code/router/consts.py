from os import environ, sep
from pathlib import Path
from socket import getfqdn

from std2.ipaddress import (
    LINK_LOCAL_V4,
    LINK_LOCAL_V6,
    LOOPBACK_V4,
    LOOPBACK_V6,
    PRIVATE_V4,
    PRIVATE_V6,
)

USER = environ["USER"]
SERVER_NAME = getfqdn()

SHORT_DURATION = 1
PRIVATE_ADDRS = (
    LOOPBACK_V4,
    LOOPBACK_V6,
    LINK_LOCAL_V4,
    LINK_LOCAL_V6,
    *PRIVATE_V4,
    PRIVATE_V6,
)

_TOP_LV = Path(__file__).resolve().parent
J2 = _TOP_LV / "j2"

_SRV = Path(sep, "srv")

TEMPLATES = _SRV / "templates"
RUN = _SRV / "run"

CONFIG = Path(sep, "config")
DEFAULT_CONFIG = RUN / "defaults.yml"
DATA = Path(sep, "data")

_TMP = Path(sep, "tmp")


NETWORKS_JSON = _SRV / "run" / "networks" / "networks.json"
IPV6_JSON = _TMP / "ipv6.json"

UNBOUND_CTL = RUN / "unbound" / "ctl.sh"
QR_DIR = RUN / "qr"
LEASES = DATA / "dnsmasq" / "leases"
