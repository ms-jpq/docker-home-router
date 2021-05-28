from dataclasses import dataclass
from hashlib import sha256
from ipaddress import IPv4Interface, IPv6Interface, ip_interface
from pathlib import PurePath
from shutil import rmtree
from subprocess import check_output, run
from typing import Any, Iterable, Iterator, Mapping, MutableSet, Tuple

from .consts import DATA, J2, QR_DIR, WG_DOMAIN, WG_PEERS, WG_PORT
from .ip import ipv6_enabled
from .render import j2_build, j2_render
from .types import Networks

_CLIENT_TPL = PurePath("wg", "client.conf")


_WG_DATA = DATA / "wireguard"
_SRV_KEY = _WG_DATA / "server.key"
_CLIENT_KEYS = _WG_DATA / "clients"


@dataclass(frozen=True)
class _Server:
    private_key: str
    public_key: str
    v4: IPv4Interface
    v6: IPv6Interface


@dataclass(frozen=True)
class _Client:
    name: str
    private_key: str
    public_key: str
    shared_key: str
    v4: IPv4Interface
    v6: IPv6Interface


def _srv(networks: Networks) -> _Server:
    _SRV_KEY.parent.mkdir(parents=True, exist_ok=True)

    wg = networks.wireguard
    v4 = ip_interface(f"{next(iter(wg.v4))}/{wg.v4.max_prefixlen}")
    v6 = ip_interface(f"{next(iter(wg.v6))}/{wg.v6.max_prefixlen}")

    if not _SRV_KEY.exists():
        pk = check_output(("wg", "genkey"), text=True).rstrip()
        _SRV_KEY.write_text(pk)

    private_key = _SRV_KEY.read_text()
    public_key = check_output(("wg", "pubkey"), input=private_key, text=True).rstrip()

    srv = _Server(
        private_key=private_key,
        public_key=public_key,
        v4=v4,
        v6=v6,
    )
    return srv


def _ip_gen(
    peers: Iterable[str], networks: Networks
) -> Iterator[Tuple[IPv4Interface, IPv6Interface]]:
    srv = _srv(networks)
    wg_v4, wg_v6 = networks.wireguard.v4, networks.wireguard.v6
    seen = {srv.v4, srv.v6}

    for peer in peers:
        hashed = int(sha256(peer.encode()).hexdigest(), 16)
        v4 = wg_v4[1]
        v6 = wg_v6[1]
        yield v4, v6


def clients(networks: Networks) -> Iterator[_Client]:
    _CLIENT_KEYS.mkdir(parents=True, exist_ok=True)

    for peer, (v4, v6) in zip(WG_PEERS, _ip_gen(WG_PEERS, networks=networks)):
        key_p, psk_p = _CLIENT_KEYS / f"{peer}.key", _CLIENT_KEYS / f"{peer}.psk"

        if key_p.exists():
            private_key = key_p.read_text()
        else:
            private_key = check_output(("wg", "genkey"), text=True).rstrip()
            key_p.write_text(private_key)

        if psk_p.exists():
            shared_key = psk_p.read_text()
        else:
            shared_key = check_output(("wg", "genpsk"), text=True).rstrip()
            psk_p.write_text(shared_key)

        public_key = check_output(
            ("wg", "pubkey"), input=private_key, text=True
        ).rstrip()

        client = _Client(
            name=peer,
            private_key=private_key,
            public_key=public_key,
            shared_key=shared_key,
            v4=v4,
            v6=v6,
        )
        yield client


def gen_qr(networks: Networks) -> None:
    j2 = j2_build(J2)

    try:
        rmtree(QR_DIR)
    except FileNotFoundError:
        pass
    QR_DIR.mkdir(parents=True, exist_ok=True)

    srv = _srv(networks)
    stack = networks.wireguard

    g_env = {
        "IPV6_ENABLED": ipv6_enabled(),
        "SERVER_PUBLIC_KEY": srv.public_key,
        "DNS_ADDR_V4": srv.v4,
        "DNS_ADDR_V6": srv.v6,
        "WG_NETWORK_V4": stack.v4,
        "WG_NETWORK_V6": stack.v6,
        "TOR_NETWORK_V4": networks.tor.v4,
        "TOR_NETWORK_V6": networks.tor.v6,
        "LAN_NETWORK_V4": networks.lan.v4,
        "LAN_NETWORK_V6": networks.lan.v6,
        "GUEST_NETWORK_V4": networks.guest.v4,
        "GUEST_NETWORK_V6": networks.guest.v6,
        "WG_DOMAIN": WG_DOMAIN,
        "WG_PORT": WG_PORT,
    }

    for client in clients(networks):
        conf_path = (QR_DIR / client.name).with_suffix(".conf")
        qr_path = (QR_DIR / client.name).with_suffix(".png")

        l_env: Mapping[str, Any] = {
            "NAME": client.name,
            "CLIENT_PRIVATE_KEY": client.private_key,
            "SHARED_KEY": client.shared_key,
            "CLIENT_ADDR_V4": client.v4,
            "CLIENT_ADDR_V6": client.v6,
        }
        env = {**l_env, **g_env}
        text = j2_render(j2, path=_CLIENT_TPL, env=env)
        conf_path.write_text(text)

        run(
            ("qrencode", "--output", str(qr_path)), input=text.encode()
        ).check_returncode()


def wg_env(networks: Networks) -> Mapping[str, Any]:
    srv = _srv(networks)
    peers = (
        {
            "NAME": client.name,
            "PUBLIC_KEY": client.public_key,
            "SHARED_KEY": client.shared_key,
            "V4_ADDR": client.v4,
            "V6_ADDR": client.v6,
        }
        for client in clients(networks)
    )
    env = {
        "SERVER_PRIVATE_KEY": srv.private_key,
        "PORT": WG_PORT,
        "PEERS": peers,
    }
    return env
