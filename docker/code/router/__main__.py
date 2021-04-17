from argparse import ArgumentParser, Namespace

from std2.pathlib import walk

from .consts import RUN, TEMPLATES
from .template import j2_build, j2_render


def _template() -> None:
    env = {}
    j2 = j2_build(TEMPLATES)
    for path in walk(TEMPLATES):
        tpl = path.relative_to(TEMPLATES)
        dest = RUN / tpl
        text = j2_render(j2, path=tpl, env=env)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text)


def _parse_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("op", choices=("template",))
    return parser.parse_args()


def main() -> None:
    args = _parse_args()

    if args.op == "template":
        _template()


main()
