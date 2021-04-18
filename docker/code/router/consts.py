from os import environ
from pathlib import Path

LFS = ","

_SRV = Path("/", "srv")

TEMPLATES = _SRV / Path("templates")
RUN = _SRV / Path("run")

NETWORKS = RUN / "networks.json"


IP6_ULA_GLOBAL = environ["IP6_ULA_GLOBAL"]

WAN_IF = environ["WAN_IF"]
LAN_IF = environ["LAN_IF"]
GUEST_IF = environ["GUEST_IF"]

IP6_ULA_GLOBAL = environ["IP6_ULA_GLOBAL"]
IP6_ULA_SUBNET_EXCLUSION = environ["IP6_ULA_SUBNET_EXCLUSION"]
IP4_EXCLUSION = environ["IP4_EXCLUSION"]

DNS_SERVERS = environ["DNS_SERVERS"]
NTP_SERVERS = environ["NTP_SERVERS"]
