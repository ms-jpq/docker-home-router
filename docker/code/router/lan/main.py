from argparse import ArgumentParser, Namespace
from ipaddress import IPv4Address, ip_address
from string import Template
from subprocess import check_call
from sys import stderr
from typing import Sequence, Tuple

from std2.types import IPAddress

from ..consts import LAN_DOMAIN, LOCAL_TTL, SHORT_DURATION, UNBOUND_CONF
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


def _mod(op: str, *args: str) -> None:
    check_call(
        ("unbound-control", "-c", str(UNBOUND_CONF), op, *args), timeout=SHORT_DURATION
    )
    print(op, *args, file=stderr)


def _add(hostname: str, addr: IPAddress) -> None:
    zone, ptr, na = _parse(hostname, addr=addr)
    _mod("local_zone", zone, _ZONE_TYPE)
    _mod("local_data", ptr)
    _mod("local_data", na)


def _rm(hostname: str, addr: IPAddress) -> None:
    zone, ptr, na = _parse(hostname, addr=addr)
    _mod("local_zone_remove", zone)
    _mod("local_zones_remove", ptr)
    _mod("local_zones_remove", na)


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
    if args.hostname:
        if args.op in {"old", "add"}:
            _add(args.hostname, addr=addr)
        elif args.op in {"del"}:
            _rm(args.hostname, addr=addr)
        else:
            assert False
