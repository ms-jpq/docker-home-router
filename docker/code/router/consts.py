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

DNSMASQ_PID = Path("tmp", "dnsmasq-lan.pid")


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
IF_EXCLUSIONS = frozenset(split(environ["IF_EXCLUSIONS"]))

TC_INGRESS = tuple(split(environ["TC_INGRESS"]))
TC_EGRESS = tuple(split(environ["TC_EGRESS"]))


LOOPBACK_EXCLUSION = frozenset(map(IPv4Network, split(environ["LOOPBACK_EXCLUSION"])))
IP6_ULA_GLOBAL = environ["IP6_ULA_GLOBAL"]
IP6_ULA_SUBNET_EXCLUSION = frozenset(split(environ["IP6_ULA_SUBNET_EXCLUSION"]))
IP4_EXCLUSION = frozenset(map(IPv4Network, split(environ["IP4_EXCLUSION"])))
IP4_PREFIX = clamp(16, int(environ["IP4_PREFIX"]), 24)
TOR_IP4_PREFIX = 16


DHCP_LEASE_TIME = clamp(2, int(environ["DHCP_LEASE_TIME"]), 24 * 7)
DNS_SERVERS = frozenset(split(environ["DNS_SERVERS"]))
LAN_DOMAIN = environ["LAN_DOMAIN"]


WG_DOMAIN = environ["WG_DOMAIN"] or SERVER_NAME
WG_PEERS = frozenset(split(environ["WG_PEERS"]))


TIMEOUT = 1
