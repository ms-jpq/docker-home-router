from concurrent.futures import ThreadPoolExecutor
from ipaddress import IPv4Address
from itertools import chain
from json import loads
from locale import strxfrm
from pathlib import Path
from subprocess import Popen
from tempfile import TemporaryDirectory
from threading import Lock
from time import sleep
from typing import Iterator, MutableMapping, MutableSet, Tuple

from jinja2 import Environment
from std2.concurrent.futures import gather
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


def _proc() -> Popen:
    return Popen(("dnsmasq", "--conf-dir", "/srv/run/dnsmasq/lan"))


def _p_peers() -> Iterator[Tuple[str, IPAddress]]:
    WG_PEERS_JSON.parent.mkdir(parents=True, exist_ok=True)
    WG_PEERS_JSON.touch()
    json = loads(WG_PEERS_JSON.read_text() or "{}")
    peers: WGPeers = decode(WGPeers, json, decoders=BUILTIN_DECODERS)
    for name, addrs in peers.items():
        yield name, addrs.v4
        yield name, addrs.v6


def _poll(j2: Environment) -> bool:
    dyn = DYN.read_text()
    addn = ADDN_HOSTS.read_text()

    networks = load_networks()
    mappings: MutableMapping[str, MutableSet[IPAddress]] = {}
    for name, addr in chain(leases(networks), _p_peers()):
        acc = mappings.setdefault(name, set())
        acc.add(addr)

    env = {
        "MAPPINGS": {
            key: sorted(mappings[key], key=lambda i: isinstance(i, IPv4Address))
            for key in sorted(mappings, key=strxfrm)
        },
        "LAN_DOMAIN": LAN_DOMAIN,
    }
    t1 = j2_render(j2, path=_DYN, env=env)
    t2 = j2_render(j2, path=_ADDN_HOSTS, env=env)
    needs_restart = dyn != t1

    if addn != t2:
        with TemporaryDirectory() as temp:
            tmp = Path(temp) / "tmp"
            tmp.write_text(t2)
            tmp.rename(ADDN_HOSTS)

    if needs_restart:
        DYN.write_text(t1)

    return needs_restart


def main() -> None:
    j2 = j2_build(J2)
    lock = Lock()
    proc = _proc()

    def l1() -> None:
        nonlocal proc
        while True:
            needs_restart = _poll(j2)
            if needs_restart:
                with lock:
                    proc.terminate()
            sleep(2)

    def l2() -> None:
        nonlocal proc
        while True:
            proc.wait()
            with lock:
                proc = _proc()

    with ThreadPoolExecutor() as pool:
        f1 = pool.submit(l1)
        f2 = pool.submit(l2)
        gather(f1, f2)
