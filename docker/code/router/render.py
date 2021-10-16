from os.path import normcase
from pathlib import Path, PurePath
from typing import Any, Mapping

from jinja2 import Environment, FileSystemLoader, StrictUndefined


def j2_build(*base: Path) -> Environment:
    j2 = Environment(
        enable_async=False,
        trim_blocks=True,
        lstrip_blocks=True,
        undefined=StrictUndefined,
        loader=FileSystemLoader(base, followlinks=True),
    )
    return j2


def j2_render(j2: Environment, path: PurePath, env: Mapping[str, Any]) -> str:
    text = j2.get_template(normcase(path)).render(env)
    return text
