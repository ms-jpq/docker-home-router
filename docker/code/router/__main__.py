from argparse import ArgumentParser, Namespace
from typing import Any, Mapping

from std2.pathlib import walk

from .cake.main import main as cake_main
from .consts import (
    DNS_SERVERS,
    GUEST_IF,
    LAN_IF,
    LFS,
    NTP_SERVERS,
    RUN,
    TEMPLATES,
    USER,
    WAN_IF,
    WG_IF,
)
from .dnsmasq.main import main as dnsmasq_main
from .subnets import calculate_networks, dump_networks, load_networks
from .template import j2_build, j2_render
from .types import Networks
from .unbound.main import main as unbound_main
from .wireguard.main import main as wg_main


def _env(networks: Networks) -> Mapping[str, Any]:
    env = {
        "USER": USER,
        "WAN_IF": WAN_IF,
        "LAN_IF": LAN_IF,
        "GUEST_IF": GUEST_IF,
        "WG_IF": WG_IF,
        "GUEST_NETWORK_V4": networks.guest.v4,
        "GUEST_NETWORK_V6": networks.guest.v6,
        "LAN_NETWORK_V4": networks.lan.v4,
        "LAN_NETWORK_V6": networks.lan.v6,
        "TOR_NETWORK_V4": networks.tor.v4,
        "TOR_NETWORK_V6": networks.tor.v6,
        "WG_NETWORK_V4": networks.wireguard.v4,
        "WG_NETWORK_V6": networks.wireguard.v6,
        "DNS_SERVERS": DNS_SERVERS.split(LFS),
        "NTP_SERVERS": NTP_SERVERS.split(LFS),
    }
    return env


def _template() -> None:
    try:
        networks = load_networks()
    except Exception:
        networks = calculate_networks()

    dump_networks(networks)

    env = _env(networks)
    j2 = j2_build(TEMPLATES)
    for path in walk(TEMPLATES):
        tpl = path.relative_to(TEMPLATES)
        dest = RUN / tpl
        text = j2_render(j2, path=tpl, env=env)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text)


def _parse_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("op", choices=("template", "cake", "wg", "dnsmasq", "unbound"))
    return parser.parse_args()


def main() -> None:
    args = _parse_args()

    if args.op == "template":
        _template()
    elif args.op == "cake":
        cake_main()
    elif args.op == "wg":
        wg_main()
    elif args.op == "dnsmasq":
        dnsmasq_main()
    elif args.op == "unbound":
        unbound_main()
    else:
        assert False


main()
