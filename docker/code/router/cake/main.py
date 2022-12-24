from subprocess import check_call

from ..ip import link_show
from ..options.parser import settings

TC_IFB = f"ifb4{settings().interfaces.wan}"

_RX_OPTS = (
    "ingress",
    "nat",
    "dual-dsthost",
    *settings().traffic_control.receive,
)

_TX_OPTS = (
    "egress",
    "nat",
    "dual-srchost",
    *settings().traffic_control.transmit,
)


_QDISC_ID = "ffff:"


def _tx(wan_if: str) -> None:
    check_call(
        (
            "tc",
            "qdisc",
            "replace",
            "dev",
            wan_if,
            "root",
            "cake",
            *_TX_OPTS,
        )
    )


def _rx(wan_if: str) -> None:
    if TC_IFB not in link_show("ifb"):
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
            *_RX_OPTS,
        )
    )
    check_call(("ip", "link", "set", "up", "dev", TC_IFB))
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
    _tx(settings().interfaces.wan)
    _rx(settings().interfaces.wan)
