from argparse import ArgumentParser, Namespace
from typing import Sequence, Tuple

from .cake.main import main as cake_main
from .dhclient.main import main as dhclient_main
from .domains.main import main as domains_main
from .ifup.main import main as ifup_main
from .stats.main import main as stats_main
from .template.main import main as template_main
from .wireguard.main import main as wg_main
from .nat64.main import main as nat_main


def _parse_args() -> Tuple[Namespace, Sequence[str]]:
    parser = ArgumentParser()
    parser.add_argument(
        "op",
        choices=(
            "cake",
            "dhclient",
            "domains",
            "ifup",
            "nat64",
            "stats",
            "template",
            "wg",
        ),
    )
    return parser.parse_known_args()


def main() -> None:
    args, argv = _parse_args()

    if args.op == "ifup":
        ifup_main()
    elif args.op == "cake":
        cake_main()
    elif args.op == "dhclient":
        dhclient_main()
    elif args.op == "domains":
        domains_main(argv)
    elif args.op == "stats":
        stats_main()
    elif args.op == "template":
        template_main()
    elif args.op == "wg":
        wg_main()
    elif args.op == "nat64":
        nat_main()
    else:
        assert False, (args, argv)


main()
