from argparse import ArgumentParser, Namespace
from json import loads
from subprocess import CalledProcessError, check_call
from typing import Any, Mapping

from std2.lex import split
from std2.pathlib import walk

from .cake.main import main as cake_main
from .consts import (
    DNS_SERVERS,
    GUEST_IF,
    LAN_IF,
    NTP_SERVERS,
    RUN,
    SERVICES,
    TEMPLATES,
    USER,
    WAN_IF,
    WG_IF,
)
from .dnsmasq.lan.main import main as dns_lan_main
from .dnsmasq.leases.main import main as dns_leases_main
from .ip import ipv6_enabled
from .render import j2_build, j2_render
from .subnets import calculate_networks, dump_networks, load_networks
from .tc.main import main as tc_main
from .types import Networks
from .unbound.main import main as unbound_main
from .wireguard.main import main as wg_main


def _sysctl() -> None:
    try:
        check_call(("sysctl", "net.ipv4.ip_forward=1"))
        check_call(("sysctl", "net.ipv6.conf.all.forwarding=1"))
    except CalledProcessError:
        pass


def _env(networks: Networks) -> Mapping[str, Any]:
    if not WAN_IF:
        raise ValueError("WAN_IF - required")
    elif not LAN_IF:
        raise ValueError("LAN_IF - required")
    elif not WG_IF:
        raise ValueError("WG_IF - required")
    elif not DNS_SERVERS:
        raise ValueError("DNS_SERVERS - required")
    elif not NTP_SERVERS:
        raise ValueError("NTP_SERVERS - required")
    else:
        env = {
            "USER": USER,
            "SERVICES": loads(SERVICES.read_text()),
            "WAN_IF": WAN_IF,
            "LAN_IF": LAN_IF,
            "GUEST_IF": GUEST_IF,
            "WG_IF": WG_IF,
            "IPV6_ENABLED": ipv6_enabled(),
            "GUEST_NETWORK_V4": networks.guest.v4,
            "GUEST_NETWORK_V6": networks.guest.v6,
            "LAN_NETWORK_V4": networks.lan.v4,
            "LAN_NETWORK_V6": networks.lan.v6,
            "TOR_NETWORK_V4": networks.tor.v4,
            "TOR_NETWORK_V6": networks.tor.v6,
            "WG_NETWORK_V4": networks.wireguard.v4,
            "WG_NETWORK_V6": networks.wireguard.v6,
            "DNS_SERVERS": split(DNS_SERVERS),
            "NTP_SERVERS": split(NTP_SERVERS),
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
    parser.add_argument(
        "op",
        choices=(
            "cake",
            "dns-lan",
            "dns-leases",
            "tc",
            "template",
            "unbound",
            "wg",
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()

    if args.op == "cake":
        cake_main()
    elif args.op == "dns-lan":
        dns_lan_main()
    elif args.op == "dns-leases":
        dns_leases_main()
    elif args.op == "tc":
        tc_main()
    elif args.op == "template":
        _sysctl()
        _template()
    elif args.op == "unbound":
        unbound_main()
    elif args.op == "wg":
        wg_main()
    else:
        assert False


main()
