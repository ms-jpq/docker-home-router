from pathlib import PurePath
from shutil import rmtree
from subprocess import check_output, run
from typing import Any, Iterator, Mapping, Tuple

from .consts import DATA, J2, QR_DIR, WG_DOMAIN, WG_PEERS, WG_PORT
from .ip import ipv6_enabled
from .render import j2_build, j2_render
from .types import DualStack, Networks, WGPeer

_CLIENT_TPL = PurePath("wg", "client.conf")


_WG_DATA = DATA / "wireguard"
_SRV_KEY = _WG_DATA / "server.key"
_CLIENT_KEYS = _WG_DATA / "clients"

_PEER_KEYS = Tuple[str, str, str, str]


def _srv_keys() -> Tuple[str, str]:
    _SRV_KEY.parent.mkdir(parents=True, exist_ok=True)

    if not _SRV_KEY.exists():
        pk = check_output(("wg", "genkey"), text=True).rstrip()
        _SRV_KEY.write_text(pk)

    private_key = _SRV_KEY.read_text()
    public_key = check_output(("wg", "pubkey"), input=private_key, text=True).rstrip()
    return private_key, public_key


def _client_keys() -> Iterator[_PEER_KEYS]:
    _CLIENT_KEYS.mkdir(parents=True, exist_ok=True)

    for peer in WG_PEERS:
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
        yield peer, private_key, public_key, shared_key


def wg_peers(networks: Networks) -> Mapping[str, WGPeer]:
    stack = networks.wireguard
    hosts = zip(stack.v4.hosts(), stack.v6.hosts())
    gen = tuple(zip(_client_keys(), hosts))
    peers = {peer: WGPeer(v4=v4, v6=v6) for (peer, _, _, _), (v4, v6) in gen}
    return peers


def gen_qr(networks: Networks) -> None:
    j2 = j2_build(J2)

    try:
        rmtree(QR_DIR)
    except FileNotFoundError:
        pass
    QR_DIR.mkdir(parents=True, exist_ok=True)

    _, server_public = _srv_keys()
    stack = networks.wireguard
    hosts = zip(stack.v4.hosts(), stack.v6.hosts())
    dns_v4, dns_v6 = next(hosts)
    gen = tuple(zip(_client_keys(), hosts))

    g_env = {
        "IPV6_ENABLED": ipv6_enabled(),
        "SERVER_PUBLIC_KEY": server_public,
        "DNS_ADDR_V4": dns_v4,
        "DNS_ADDR_V6": dns_v6,
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

    for (peer, client_private, _, client_shared), (v4, v6) in gen:
        v4_addr = f"{v4}/{stack.v4.max_prefixlen}"
        v6_addr = f"{v6}/{stack.v6.max_prefixlen}"

        conf_path = (QR_DIR / peer).with_suffix(".conf")
        qr_path = (QR_DIR / peer).with_suffix(".png")

        l_env: Mapping[str, Any] = {
            "CLIENT_PRIVATE_KEY": client_private,
            "SHARED_KEY": client_shared,
            "CLIENT_ADDR_V4": v4_addr,
            "CLIENT_ADDR_V6": v6_addr,
        }
        env = {**l_env, **g_env}
        text = j2_render(j2, path=_CLIENT_TPL, env=env)
        conf_path.write_text(text)

        run(
            ("qrencode", "--output", str(qr_path)), input=text.encode()
        ).check_returncode()


def wg_env(stack: DualStack) -> Mapping[str, Any]:
    server_private, _ = _srv_keys()
    hosts = zip(stack.v4.hosts(), stack.v6.hosts())
    next(hosts)
    peers = (
        {
            "PUBLIC_KEY": peer_public,
            "SHARED_KEY": peer_shared,
            "V4_ADDR": f"{v4}/{stack.v4.max_prefixlen}",
            "V6_ADDR": f"{v6}/{stack.v6.max_prefixlen}",
        }
        for (_, _, peer_public, peer_shared), (v4, v6) in zip(_client_keys(), hosts)
    )
    env = {
        "SERVER_PRIVATE_KEY": server_private,
        "PORT": WG_PORT,
        "PEERS": peers,
    }
    return env
