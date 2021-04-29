from argparse import ArgumentParser, Namespace
from shutil import copystat
from subprocess import CalledProcessError, check_call
from typing import Any, Mapping

from std2.lex import split
from std2.pathlib import walk

from .cake.main import main as cake_main
from .consts import (
    DNS_SERVERS,
    GUEST_IF,
    LAN_IF,
    LOOPBACK,
    LOOPBACK_LOCAL,
    NTP_SERVERS,
    RUN,
    STATS_PORT,
    TEMPLATES,
    USER,
    WAN_IF,
    WG_IF,
)
from .dnsmasq.main import main as dnsmsq_main
from .ifup.main import main as ifup_main
from .ip import ipv6_enabled
from .port_fwd import forwarded_ports
from .render import j2_build, j2_render
from .stats.main import main as stats_main
from .subnets import calculate_networks, load_networks
from .types import Networks
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
            "STATS_PORT": STATS_PORT,
            "LOOPBACK": LOOPBACK,
            "LOOPBACK_LOCAL": LOOPBACK_LOCAL,
            "FORWARDED_PORTS": forwarded_ports(),
        }
        return env


def _template() -> None:
    try:
        networks = load_networks()
    except Exception:
        networks = calculate_networks()

    env = _env(networks)
    j2 = j2_build(TEMPLATES)
    for path in walk(TEMPLATES):
        tpl = path.relative_to(TEMPLATES)
        dest = (RUN / tpl).resolve()
        dest.parent.mkdir(parents=True, exist_ok=True)
        if path.is_symlink():
            dest.unlink(missing_ok=True)
            dest.symlink_to(path.resolve())
        else:
            text = j2_render(j2, path=tpl, env=env)
            dest.write_text(text)
            copystat(path, dest)


def _parse_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument(
        "op",
        choices=(
            "ifup",
            "cake",
            "dnsmasq",
            "stats",
            "template",
            "wg",
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()

    if args.op == "ifup":
        ifup_main()
    elif args.op == "cake":
        cake_main()
    elif args.op == "dnsmasq":
        dnsmsq_main()
    elif args.op == "stats":
        stats_main()
    elif args.op == "template":
        _sysctl()
        _template()
    elif args.op == "wg":
        wg_main()
    else:
        assert False


main()
