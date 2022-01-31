from argparse import ArgumentParser, Namespace
from typing import Sequence, Tuple

from .cache.main import main as cache_main
from .cake.main import main as cake_main
from .dhclient_pd.main import main as dhclient_pd_main
from .dhclient_script.main import main as dhclient_script
from .domains.main import main as domains_main
from .ifup.main import main as ifup_main
from .stats.main import main as stats_main
from .template.main import main as template_main
from .wireguard.main import main as wg_main


def _parse_args() -> Tuple[Namespace, Sequence[str]]:
    parser = ArgumentParser()
    parser.add_argument(
        "op",
        choices=(
            "cache",
            "cake",
            "dh_client",
            "dh_script",
            "domains",
            "ifup",
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
    elif args.op == "cache":
        cache_main()
    elif args.op == "cake":
        cake_main()
    elif args.op == "dh_client":
        dhclient_pd_main()
    elif args.op == "dh_script":
        dhclient_script()
    elif args.op == "domains":
        domains_main(argv)
    elif args.op == "stats":
        stats_main()
    elif args.op == "template":
        template_main()
    elif args.op == "wg":
        wg_main()
    else:
        assert False


main()
