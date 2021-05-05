from ipaddress import IPv4Network
from os import environ
from pathlib import Path
from socket import getfqdn

from std2.lex import split
from std2.ordinal import clamp

SERVER_NAME = getfqdn()

_TOP_LV = Path(__file__).resolve().parent
J2 = _TOP_LV / "j2"

_SRV = Path("/", "srv")
DATA = Path("/", "data")
_CONFIG = Path("/", "config")

TEMPLATES = _SRV / Path("templates")
RUN = _SRV / Path("run")

PORT_FWD = _CONFIG / "port_fwd"

LEASES = DATA / "dnsmasq" / "leases"
_DNSMASQ = RUN / "dnsmasq"
DYN = _DNSMASQ / "lan" / "5-dyn.conf"
ADDN_HOSTS = _DNSMASQ / "hosts" / "addrs.conf"

NETWORKS_JSON = _SRV / "run" / "networks" / "networks.json"
WG_PEERS_JSON = RUN / "wireguard" / "wg-peers.json"

UNBOUND_CONF = RUN / "unbound" / "0-include.conf"


UNBOUND_PORT = 5335
WG_PORT = clamp(1, int(environ["WG_PORT"]), 2 ** 16 - 1)
STATS_PORT = clamp(1025, int(environ["STATS_PORT"]), 2 ** 16 - 1)
SQUID_PORT = clamp(1025, int(environ["SQUID_PORT"]), 2 ** 16 - 1)
TOR_PORT = clamp(1025, int(environ["TOR_PORT"]), 2 ** 16 - 1)

USER = environ["USER"]

WAN_IF = environ["WAN_IF"]
LAN_IF = environ["LAN_IF"]
GUEST_IF = environ["GUEST_IF"]
WG_IF = environ["WG_IF"]
IF_EXCLUSIONS = tuple(split(environ["IF_EXCLUSIONS"]))

IP6_ULA_GLOBAL = environ["IP6_ULA_GLOBAL"]
IP6_ULA_SUBNET_EXCLUSION = tuple(split(environ["IP6_ULA_SUBNET_EXCLUSION"]))
IP4_EXCLUSION = tuple(map(IPv4Network, split(environ["IP4_EXCLUSION"])))
IP4_PREFIX = clamp(16, int(environ["IP4_PREFIX"]), 24)
TOR_IP4_PREFIX = 16

LEASE_TIME = clamp(2, int(environ["LEASE_TIME"]), 24 * 7)
DNS_SERVERS = tuple(split(environ["DNS_SERVERS"]))
NTP_SERVERS = tuple(split(environ["NTP_SERVERS"]))

WG_PEERS = environ["WG_PEERS"]

WAN_DOMAIN = environ["WAN_DOMAIN"] or SERVER_NAME
LAN_DOMAIN = environ["LAN_DOMAIN"]

LOOPBACK_EXCLUSION = tuple(map(IPv4Network, split(environ["LOOPBACK_EXCLUSION"])))

TIMEOUT = 1
