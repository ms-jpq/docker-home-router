from json import loads
from subprocess import check_call, check_output



_EGRESS_OPTS = (
    "egress",
    "nat",
    "dual-srchost",
    "besteffort",
    "wash",
    "ethernet",
    "rtt",
    "100ms",
)

_INGRESS_OPTS = (
    "ingress",
    "dual-dsthost",
    "besteffort",
    "wash",
    "ethernet",
    "rtt",
    "10ms",
)

_QDISC_ID = "ffff:"


def _egress(wan_if: str) -> None:
    check_call(("tc", "qdisc", "replace", "dev", wan_if, "root", "cake", *_EGRESS_OPTS))


def _ingress(wan_if: str) -> None:
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
        ("tc", "qdisc", "replace", "dev", link_name, "root", "cake", *_INGRESS_OPTS)
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
    wan_if = _WAN_IF.read_text().rstrip()
    _egress(wan_if)
    _ingress(wan_if)


main()

