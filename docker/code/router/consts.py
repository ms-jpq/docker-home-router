from os import environ
from pathlib import Path
from socket import getfqdn

_TOP_LV = Path(__file__).resolve().parent

_SRV = Path("/", "srv")
DATA = Path("/", "data")

J2 = _TOP_LV / "j2"

TEMPLATES = _SRV / Path("templates")
RUN = _SRV / Path("run")

LEASES = DATA / "dnsmasq" / "leases"
DYN = RUN / "dnsmasq" / "lan" / "5-dyn.conf"

UNBOUND_CONF = RUN / "unbound" / "0-include.conf"

NETWORKS_JSON = _SRV / "run" / "networks" / "networks.json"
WG_PEERS_JSON = RUN / "wireguard" / "wg-peers.json"

STATS_PORT = int(environ["STATS_PORT"])
USER = environ["USER"]

WAN_IF = environ["WAN_IF"]
LAN_IF = environ["LAN_IF"]
GUEST_IF = environ["GUEST_IF"]
WG_IF = environ["WG_IF"]

IP6_ULA_GLOBAL = environ["IP6_ULA_GLOBAL"]
IP6_ULA_SUBNET_EXCLUSION = environ["IP6_ULA_SUBNET_EXCLUSION"]
IP4_EXCLUSION = environ["IP4_EXCLUSION"]

DNS_SERVERS = environ["DNS_SERVERS"]
NTP_SERVERS = environ["NTP_SERVERS"]

WG_PEERS = environ["WG_PEERS"]
SERVER_NAME = environ["SERVER_NAME"] or getfqdn()

TIMEOUT = 1
