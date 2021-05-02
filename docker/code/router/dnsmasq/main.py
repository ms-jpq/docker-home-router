from itertools import chain
from json import loads
from locale import strxfrm
from pathlib import Path
from subprocess import check_call
from tempfile import TemporaryDirectory
from time import sleep
from typing import Iterator, MutableMapping, MutableSet, Optional, Tuple

from jinja2 import Environment
from std2.pickle import decode
from std2.pickle.coders import BUILTIN_DECODERS
from std2.types import IPAddress

from ..consts import ADDN_HOSTS, DYN, J2, LAN_DOMAIN, WG_PEERS_JSON
from ..leases import leases
from ..render import j2_build, j2_render
from ..subnets import load_networks
from ..types import WGPeers

_DYN = Path("dns", "5-dyn.conf")
_ADDN_HOSTS = Path("dns", "addrs.conf")
_PID_FILE = Path("/", "var", "run", "dnsmsaq-lan.pid")


def _pid() -> Optional[int]:
    try:
        pid = _PID_FILE.read_text().rstrip()
    except Exception:
        return None
    else:
        return int(pid)


def _p_peers() -> Iterator[Tuple[str, IPAddress]]:
    WG_PEERS_JSON.parent.mkdir(parents=True, exist_ok=True)
    WG_PEERS_JSON.touch()
    json = loads(WG_PEERS_JSON.read_text() or "{}")
    peers: WGPeers = decode(WGPeers, json, decoders=BUILTIN_DECODERS)
    for name, addrs in peers.items():
        yield name, addrs.v4
        yield name, addrs.v6


def _forever(j2: Environment) -> None:
    dyn = DYN.read_text()
    addn = ADDN_HOSTS.read_text()
    pid = _pid()

    networks = load_networks()
    mappings: MutableMapping[str, MutableSet[IPAddress]] = {}
    for name, addr in chain(leases(networks), _p_peers()):
        acc = mappings.setdefault(name, set())
        acc.add(addr)

    env = {
        "MAPPINGS": {key: mappings[key] for key in sorted(mappings, key=strxfrm)},
        "LAN_DOMAIN": LAN_DOMAIN,
    }
    t1 = j2_render(j2, path=_DYN, env=env)
    t2 = j2_render(j2, path=_ADDN_HOSTS, env=env)

    if addn != t2:
        with TemporaryDirectory() as temp:
            tmp = Path(temp) / "tmp"
            tmp.write_text(t2)
            tmp.rename(ADDN_HOSTS)

    if pid and dyn != t1:
        DYN.write_text(t1)
        check_call(("kill", str(pid)))


def main() -> None:
    j2 = j2_build(J2)
    while True:
        _forever(j2)
        sleep(2)
