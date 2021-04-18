from os import environ
from pathlib import Path

_TOP_LV = Path(__file__).resolve().parent

_SRV = Path("/", "srv")
DATA = Path("/", "data")

J2 = _TOP_LV / "j2"

TEMPLATES = _SRV / Path("templates")
RUN = _SRV / Path("run")

NETWORKS = DATA / "networks.json"

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
