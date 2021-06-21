from argparse import ArgumentParser, Namespace
from ipaddress import IPv4Address, ip_address
from os import environ, linesep
from string import Template
from subprocess import run
from sys import stderr
from typing import Sequence, Tuple

from std2.types import IPAddress

from ..consts import LAN_DOMAIN, LOCAL_TTL, SHORT_DURATION, UNBOUND_CTL
from ..records import encode_dns

_ZONE_TYPE = "redirect"
_LOCAL_ZONE = Template(f"$HOSTNAME.{LAN_DOMAIN}.")
_LOCAL_DATA_PTR = Template(f"$RDDA. {LOCAL_TTL} IN PTR $HOSTNAME.{LAN_DOMAIN}.")
_LOCAL_DATA_A = Template(f"$HOSTNAME.{LAN_DOMAIN}. {LOCAL_TTL} IN A $ADDR")
_LOCAL_DATA_AAAA = Template(f"$HOSTNAME.{LAN_DOMAIN}. {LOCAL_TTL} IN AAAA $ADDR")


def _parse(hostname: str, addr: IPAddress) -> Tuple[str, str, str]:
    hostname = encode_dns(hostname)
    zone = _LOCAL_ZONE.substitute(HOSTNAME=hostname)
    ptr = _LOCAL_DATA_PTR.substitute(HOSTNAME=hostname, RDDA=addr.reverse_pointer)
    na = (
        _LOCAL_DATA_A.substitute(HOSTNAME=hostname, ADDR=addr)
        if isinstance(addr, IPv4Address)
        else _LOCAL_DATA_AAAA.substitute(HOSTNAME=hostname, ADDR=addr)
    )
    return zone, ptr, na


def _ctl(op: str, *args: str) -> None:
    stdin = (linesep.join(args) + linesep).encode()
    run((str(UNBOUND_CTL), op), input=stdin, timeout=SHORT_DURATION).check_returncode()


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
    parser.add_argument("op", choices=("old", "add", "del"))
    parser.add_argument("mac")
    parser.add_argument("ip")
    parser.add_argument("hostname", nargs="?")
    return parser.parse_args(args)


def main(argv: Sequence[str]) -> None:
    args = _parse_args(argv)
    addr: IPAddress = ip_address(args.ip)
    hostname = environ.get("DNSMASQ_SUPPLIED_HOSTNAME", args.hostname)
    if hostname:
        if args.op in {"old", "add"}:
            _add(hostname, addr=addr)
        elif args.op in {"del"}:
            _rm(hostname, addr=addr)
        else:
            assert False

