from ipaddress import IPv4Network
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
from std2.lex import split
from std2.ordinal import clamp

SERVER_NAME = getfqdn()

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
_CONFIG = Path(sep, "config")
_TMP = Path(sep, "tmp")
DATA = Path(sep, "data")

TEMPLATES = _SRV / Path("templates")
RUN = _SRV / Path("run")

PORT_FWD = _CONFIG / "port_fwd"

LEASES = DATA / "dnsmasq" / "leases"


NETWORKS_JSON = _SRV / "run" / "networks" / "networks.json"
QR_DIR = RUN / "qr"


IPV6_STAT = _TMP / "ipv6.json"

WG_PORT = clamp(1, int(environ["WG_PORT"]), 2 ** 16 - 1)
STATS_PORT = clamp(1025, int(environ["STATS_PORT"]), 2 ** 16 - 1)
SQUID_PORT = clamp(1025, int(environ["SQUID_PORT"]), 2 ** 16 - 1)
TOR_PORT = clamp(1025, int(environ["TOR_PORT"]), 2 ** 16 - 1)

USER = environ["USER"]

WAN_IF = environ["WAN_IF"]
LAN_IF = environ["LAN_IF"]
GUEST_IF = environ["GUEST_IF"]
WG_IF = environ["WG_IF"]
IF_EXCLUSIONS = frozenset(split(environ["IF_EXCLUSIONS"]))

TC_INGRESS = tuple(split(environ["TC_INGRESS"]))
TC_EGRESS = tuple(split(environ["TC_EGRESS"]))
TC_IFB = f"ifb4{WAN_IF}"

LOOPBACK_EXCLUSION = frozenset(map(IPv4Network, split(environ["LOOPBACK_EXCLUSION"])))
IP6_ULA_GLOBAL = environ["IP6_ULA_GLOBAL"]
IP4_EXCLUSION = frozenset(map(IPv4Network, split(environ["IP4_EXCLUSION"])))
IP4_PREFIX = clamp(16, int(environ["IP4_PREFIX"]), 24)
TOR_IP4_PREFIX = 16


DHCP_LEASE_TIME = clamp(2, int(environ["DHCP_LEASE_TIME"]), 24 * 7)
LOCAL_TTL = max(0, int(environ["LOCAL_TTL"]))
DNSSEC = bool(int(environ["DNSSEC"]))
DNS_SERVERS = frozenset(split(environ["DNS_SERVERS"]))
LAN_DOMAIN = environ["LAN_DOMAIN"]


WG_DOMAIN = environ["WG_DOMAIN"] or SERVER_NAME
WG_PEERS = frozenset(split(environ["WG_PEERS"]))


SHORT_DURATION = 1
