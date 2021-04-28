from itertools import chain
from typing import Any, Mapping, MutableMapping, MutableSequence, Sequence, Union

from std2.pickle import decode
from yaml import safe_load

from .consts import PORT_FWD
from .types import Forwards


def forwarded_ports() -> Mapping[str, Sequence[Mapping[str, Union[str, int]]]]:
    PORT_FWD.parent.mkdir(parents=True, exist_ok=True)

    acc: MutableMapping[str, Any] = {}
    for path in chain(PORT_FWD.glob("*.yaml"), PORT_FWD.glob("*.yml")):
        raw = path.read_text()
        yaml = safe_load(raw)
        acc.update(yaml)

    forwards: Forwards = decode(Forwards, acc, strict=False)
    fwds: MutableMapping[str, MutableSequence[Mapping[str, Union[str, int]]]] = {}

    for hostname, fws in forwards.items():
        specs = fwds.setdefault(hostname, [])
        for fw in fws:
            spec = {
                "PROTO": fw.proto,
                "FROM_PORT": fw.from_port,
                "TO_PORT": fw.to_port,
                "PROXY_PROTO": fw.proxy_proto,
            }
            specs.append(spec)
    return fwds
