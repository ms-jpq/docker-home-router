from argparse import ArgumentParser, Namespace
from ipaddress import IPv4Address, ip_address
from os import environ, linesep
from string import Template
from subprocess import run
from sys import stderr
from typing import Sequence, Tuple

from std2.ipaddress import IPAddress

from ..consts import SHORT_DURATION, UNBOUND_CTL
from ..options.parser import encode_dns_name, settings
from ..subnets import load_networks

_ZONE_TYPE = "redirect"
_LOCAL_ZONE = Template("$HOSTNAME.$DOMAIN.")
_LOCAL_DATA_PTR = Template(
    f"$RDDA. {settings().dns.local_ttl} IN PTR $HOSTNAME.$DOMAIN."
)
_LOCAL_DATA_A = Template(f"$HOSTNAME.$DOMAIN. {settings().dns.local_ttl} IN A $ADDR")
_LOCAL_DATA_AAAA = Template(
    f"$HOSTNAME.$DOMAIN. {settings().dns.local_ttl} IN AAAA $ADDR"
)


def _domain(addr: IPAddress) -> str:
    networks = load_networks()
    if addr in networks.trusted.v4 or addr in networks.trusted.v6:
        return settings().dns.local_domains.trusted
    elif addr in networks.guest.v4 or addr in networks.guest.v6:
        return settings().dns.local_domains.guest
    else:
        assert False, addr


def _parse(hostname: str, addr: IPAddress) -> Tuple[str, str, str]:
    hostname = encode_dns_name(hostname)
    domain = _domain(addr)
    zone = _LOCAL_ZONE.substitute(DOMAIN=domain, HOSTNAME=hostname)
    ptr = _LOCAL_DATA_PTR.substitute(
        DOMAIN=domain, HOSTNAME=hostname, RDDA=addr.reverse_pointer
    )
    na = (
        _LOCAL_DATA_A.substitute(DOMAIN=domain, HOSTNAME=hostname, ADDR=addr)
        if isinstance(addr, IPv4Address)
        else _LOCAL_DATA_AAAA.substitute(DOMAIN=domain, HOSTNAME=hostname, ADDR=addr)
    )
    return zone, ptr, na


def _ctl(op: str, *args: str) -> None:
    stdin = (linesep.join(args) + linesep).encode()
    run((UNBOUND_CTL, op), check=True, input=stdin, timeout=SHORT_DURATION)


def _add(hostname: str, addr: IPAddress) -> None:
    zone, ptr, na = _parse(hostname, addr=addr)
    _ctl("local_zones", f"{zone} {_ZONE_TYPE}")
    _ctl("local_datas", ptr, na)

    print("ADD", "--", hostname, addr, file=stderr)


def _rm(hostname: str, addr: IPAddress) -> None:
    zone, ptr, na = _parse(hostname, addr=addr)
    _ctl("local_zones_remove", zone)
    _ctl("local_datas_remove", ptr, na)

    print("RM ", "--", hostname, addr, file=stderr)


def _parse_args(args: Sequence[str]) -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("op", choices=("tftp", "old", "add", "del"))
    parser.add_argument("mac")
    parser.add_argument("ip")
    parser.add_argument("hostname", nargs="?")
    return parser.parse_args(args)


def main(argv: Sequence[str]) -> None:
    args = _parse_args(argv)
    addr: IPAddress = ip_address(args.ip)
    hostname = environ.get("DNSMASQ_SUPPLIED_HOSTNAME", args.hostname)
    if hostname:
        if args.op in {"tftp"}:
            pass
        elif args.op in {"old", "add"}:
            _add(hostname, addr=addr)
        elif args.op in {"del"}:
            _rm(hostname, addr=addr)
        else:
            assert False, argv
