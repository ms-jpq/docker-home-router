from ipaddress import IPv4Network
from locale import strxfrm
from os import environ, sep
from pathlib import Path
from socket import getfqdn
from typing import Iterator

from std2 import clamp
from std2.ipaddress import (
    LINK_LOCAL_V4,
    LINK_LOCAL_V6,
    LOOPBACK_V4,
    LOOPBACK_V6,
    PRIVATE_V4,
    PRIVATE_V6,
)
from std2.lex import split

_SEP, _ESC = ",", "\\"


def encode_dns(name: str) -> str:
    def cont() -> Iterator[str]:
        for char in name.encode("idna").decode():
            if char.isalnum():
                yield char
            else:
                yield "-"

    return "".join(cont())


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

TEMPLATES = _SRV / "templates"
RUN = _SRV / "run"

PORT_FWD = _CONFIG / "port_fwd"

LEASES = DATA / "dnsmasq" / "leases"
UNBOUND_CTL = RUN / "unbound" / "ctl.sh"


NETWORKS_JSON = _SRV / "run" / "networks" / "networks.json"
QR_DIR = RUN / "qr"


IPV6_STAT = _TMP / "ipv6.json"

WG_PORT = clamp(1, int(environ["WG_PORT"]), 2 ** 16 - 1)
STATS_PORT = clamp(1025, int(environ["STATS_PORT"]), 2 ** 16 - 1)
SQUID_PORT = clamp(1025, int(environ["SQUID_PORT"]), 2 ** 16 - 1)
TOR_PORT = clamp(1025, int(environ["TOR_PORT"]), 2 ** 16 - 1)

EXPOSE_STATS = int(environ["EXPOSE_STATS"])

USER = environ["USER"]

WAN_IF = environ["WAN_IF"]
LAN_IF = environ["LAN_IF"]
GUEST_IF = environ["GUEST_IF"]
WG_IF = environ["WG_IF"]
IF_EXCLUSIONS = frozenset(split(environ["IF_EXCLUSIONS"], sep=_SEP, esc=_ESC))

TC_RX = tuple(split(environ["TC_RX"], sep=_SEP, esc=_ESC))
TC_TX = tuple(split(environ["TC_TX"], sep=_SEP, esc=_ESC))
TC_IFB = f"ifb4{WAN_IF}"

LOOPBACK_EXCLUSION = frozenset(
    map(IPv4Network, split(environ["LOOPBACK_EXCLUSION"], sep=_SEP, esc=_ESC))
)
IP6_ULA_GLOBAL = environ["IP6_ULA_GLOBAL"]
IP4_EXCLUSION = frozenset(
    map(IPv4Network, split(environ["IP4_EXCLUSION"], sep=_SEP, esc=_ESC))
)
IP4_PREFIX = clamp(16, int(environ["IP4_PREFIX"]), 24)
TOR_IP4_PREFIX = 16

IPV6_PD = bool(int(environ["IPV6_PD"]))

DHCP_LEASE_TIME = clamp(1, int(environ["DHCP_LEASE_TIME"]), 24 * 7)
LOCAL_TTL = max(0, int(environ["LOCAL_TTL"]))

DNS_SEC = bool(int(environ["DNS_SEC"]))
DNS_SERVERS = frozenset(split(environ["DNS_SERVERS"], sep=_SEP, esc=_ESC))

LAN_DOMAIN = environ["LAN_DOMAIN"].encode("idna").decode()
WG_DOMAIN = environ["WG_DOMAIN"].encode("idna").decode()
GUEST_DOMAIN = environ["GUEST_DOMAIN"].encode("idna").decode()


WG_SERVER_NAME = environ["WG_SERVER_NAME"] or SERVER_NAME
WG_PEERS = sorted(
    frozenset(map(encode_dns, split(environ["WG_PEERS"], sep=_SEP, esc=_ESC))),
    key=strxfrm,
)


SHORT_DURATION = 1
