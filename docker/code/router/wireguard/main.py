from ipaddress import (
    IPv4Address,
    IPv4Network,
    IPv6Address,
    IPv6Network,
    ip_address,
    ip_network,
)
from json import loads
from os import linesep
from pathlib import Path
from shutil import rmtree
from string import Template
from subprocess import check_call, check_output, run
from typing import Iterable, Iterator, Tuple, Union

_TOP_LV = Path(__file__).resolve().parent
_SRV = _TOP_LV.parent
_CONF = _TOP_LV / "conf"
_TEMPLATES = _TOP_LV / "templates"

_SRV_CONF = _TEMPLATES / "server.conf"
_PEER_CONF = _TEMPLATES / "peer.conf"
_CLIENT_CONF = _TEMPLATES / "client.conf"

_KEYS_DIR = _TOP_LV / "keys"
_QR_DIR = _TOP_LV / "qr"
_LINK_NAME = "wg0"


_TOR_NET = _SRV / "tor_net"
_SERVER_ADDR = _CONF / "srv_addr"
_SUBNET = _CONF / "wg_net"
_DEVICES = _CONF / "devices.json"


_ADDR = Union[IPv4Address, IPv6Address]
_NETWORK = Union[IPv4Network, IPv6Network]


def _additional_networks() -> Iterator[_NETWORK]:
    if _TOR_NET.exists():
        raw = _TOR_NET.read_text().rstrip()
        yield ip_network(raw)


def _add_link() -> None:
    raw_links = check_output(("ip", "--json", "link", "show"), text=True)
    links = loads(raw_links)
    for link in links:
        if link["ifname"] == _LINK_NAME:
            break
    else:
        check_call(("ip", "link", "add", _LINK_NAME, "type", "wireguard"))


def _add_subnet(network: _NETWORK) -> None:
    raw = check_output(("ip", "--json", "address", "show", _LINK_NAME))
    addrs = loads(raw)
    for addr in addrs:
        for info in addr["addr_info"]:
            local: _ADDR = ip_address(info["local"])
            if local in network and network.prefixlen == info["prefixlen"]:
                break
        else:
            addr = f"{next(network.hosts())}/{network.prefixlen}"
            check_call(("ip", "address", "add", "dev", _LINK_NAME, addr))


def _set_up() -> None:
    check_call(("ip", "link", "set", "up", "dev", _LINK_NAME))


def _srv_keys() -> Tuple[str, str]:
    _KEYS_DIR.mkdir(parents=True, exist_ok=True)
    srv = _KEYS_DIR / "server-private.key"
    if not srv.exists():
        pk = check_output(("wg", "genkey"), text=True)
        srv.write_text(pk)

    private_key = srv.read_text().rstrip()
    public_key = check_output(("wg", "pubkey"), input=private_key, text=True).rstrip()
    return private_key, public_key


def _client_keys() -> Iterator[Tuple[Path, str, str]]:
    _KEYS_DIR.mkdir(parents=True, exist_ok=True)
    for client in sorted(_KEYS_DIR.glob("client-private-*.key")):
        path = client.relative_to(_KEYS_DIR)
        private_key = client.read_text().rstrip()
        public_key = check_output(
            ("wg", "pubkey"), input=private_key, text=True
        ).rstrip()
        yield path, private_key, public_key


def _gen_client_keys() -> None:
    for name in loads(_DEVICES.read_text()):
        path = _KEYS_DIR / f"client-private-{name}.key"
        if not path.exists():
            pk = check_output(("wg", "genkey"), text=True)
            path.write_text(pk)


def _wg_conf(network: _NETWORK) -> Iterator[str]:
    server_tpl = Template(_SRV_CONF.read_text())
    peer_tpl = Template(_PEER_CONF.read_text())

    server_private, _ = _srv_keys()
    srv = server_tpl.substitute(SERVER_PRIVATE_KEY=server_private)
    yield srv

    hosts = network.hosts()
    next(hosts)
    for (_, _, peer_public), host in zip(_client_keys(), hosts):
        addr = f"{host}/{network.max_prefixlen}"
        peer = peer_tpl.substitute(PEER_PUBLIC_KEY=peer_public, PEER_ADDR=str(addr))
        yield peer


def _gen_qr(
    server_addr: str,
    network: _NETWORK,
    lan_network: _NETWORK,
    additional_networks: Iterable[_NETWORK],
) -> None:
    client_tpl = Template(_CLIENT_CONF.read_text())
    _, server_public = _srv_keys()

    _QR_DIR.mkdir(parents=True, exist_ok=True)
    for path in _QR_DIR.iterdir():
        if path.is_symlink() or not path.is_dir():
            path.unlink()
        else:
            rmtree(path)

    hosts = network.hosts()
    dns_addr = str(next(hosts))
    for (path, client_private, _), host in zip(_client_keys(), hosts):
        addr = f"{host}/{network.max_prefixlen}"
        conf_path = (_QR_DIR / path).with_suffix(".conf")
        qr_path = (_QR_DIR / path).with_suffix(".png")

        client = client_tpl.substitute(
            SERVER_PUBLIC_KEY=server_public,
            CLIENT_PRIVATE_KEY=client_private,
            CLIENT_ADDR=addr,
            DNS_ADDR=dns_addr,
            WG_NETWORK=str(network),
            LAN_NETWORK=str(lan_network),
            MORE_NETWORKS=", ".join(map(str, additional_networks)),
            SERVER_ADDR=server_addr,
        )
        conf_path.write_text(client)
        run(
            ("qrencode", "--output", str(qr_path)), input=client.encode()
        ).check_returncode()


def _wg_up(network: _NETWORK) -> None:
    conf = linesep.join(_wg_conf(network))
    run(
        ("wg", "setconf", _LINK_NAME, "/dev/stdin"), input=conf, text=True
    ).check_returncode()


def main() -> None:
    server_addr = _SERVER_ADDR.read_text().rstrip()
    raw_subnet = _SUBNET.read_text().rstrip()
    network = ip_network(raw_subnet)
    additional_networks = tuple(_additional_networks())
    _gen_client_keys()
    _gen_qr(
        server_addr,
        network=network,
        lan_network=lan_network,
        additional_networks=additional_networks,
    )
    _add_link()
    _add_subnet(network)
    _wg_up(network)
    _set_up()
