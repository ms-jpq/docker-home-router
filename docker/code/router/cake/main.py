from json import loads
from subprocess import check_call, check_output

from ..consts import TC_TX, TC_IFB, TC_RX, WAN_IF

_INGRESS_OPTS = (
    "ingress",
    "nat",
    "dual-dsthost",
    *TC_RX,
)

_EGRESS_OPTS = (
    "egress",
    "nat",
    "dual-srchost",
    *TC_TX,
)


_QDISC_ID = "ffff:"


def _egress(wan_if: str) -> None:
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
        )
    )


def _ingress(wan_if: str) -> None:

    raw_links = check_output(("ip", "--json", "link", "show"), text=True)
    links = loads(raw_links)
    for link in links:
        if link["ifname"] == TC_IFB:
            break
    else:
        check_call(("ip", "link", "add", TC_IFB, "type", "ifb"))

    check_call(
        ("tc", "qdisc", "replace", "dev", wan_if, "handle", _QDISC_ID, "ingress")
    )
    check_call(
        (
            "tc",
            "qdisc",
            "replace",
            "dev",
            TC_IFB,
            "root",
            "cake",
            *_INGRESS_OPTS,
        )
    )
    check_call(("ip", "link", "set", TC_IFB, "up"))
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
            TC_IFB,
        )
    )


def main() -> None:
    _egress(WAN_IF)
    _ingress(WAN_IF)
