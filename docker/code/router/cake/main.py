from json import loads
from subprocess import check_call, check_output

from ..consts import WAN_IF

_EGRESS_OPTS = (
    "egress",
    "nat",
    "dual-srchost",
    "diffserv8",
    "wash",
    "ethernet",
)

_INGRESS_OPTS = (
    "ingress",
    "dual-dsthost",
    "besteffort",
    "wash",
    "ethernet",
)

_QDISC_ID = "ffff:"


def _egress(wan_if: str, rtt: str) -> None:
    check_call(
        (
            "tc",
            "qdisc",
            "replace",
            "dev",
            wan_if,
            "root",
            "cake",
            *_EGRESS_OPTS,
            "rtt",
            rtt,
        )
    )


def _ingress(wan_if: str, rtt: str) -> None:
    link_name = f"ifb4{wan_if}"

    raw_links = check_output(("ip", "--json", "link", "show"), text=True)
    links = loads(raw_links)
    for link in links:
        if link["ifname"] == link_name:
            break
    else:
        check_call(("ip", "link", "add", link_name, "type", "ifb"))

    check_call(
        ("tc", "qdisc", "replace", "dev", wan_if, "handle", _QDISC_ID, "ingress")
    )
    check_call(
        (
            "tc",
            "qdisc",
            "replace",
            "dev",
            link_name,
            "root",
            "cake",
            *_INGRESS_OPTS,
            "rtt",
            rtt,
        )
    )
    check_call(("ip", "link", "set", link_name, "up"))
    check_call(
        (
            "tc",
            "filter",
            "replace",
            "dev",
            wan_if,
            "parent",
            _QDISC_ID,
            "matchall",
            "action",
            "mirred",
            "egress",
            "redirect",
            "dev",
            link_name,
        )
    )


def main() -> None:
    _egress(WAN_IF, rtt="100ms")
    _ingress(WAN_IF, rtt="10ms")
