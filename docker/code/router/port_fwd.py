from typing import AbstractSet, Any, Mapping, MutableMapping, MutableSet, Union

from std2.pickle import decode
from yaml import safe_load

from .consts import PORT_FWD
from .types import Forwards


def port_fwd() -> Mapping[str, AbstractSet[Mapping[str, Union[str, int]]]]:
    PORT_FWD.parent.mkdir(parents=True, exist_ok=True)

    acc: MutableMapping[str, Any] = {}
    for path in PORT_FWD.glob("*.[yml|yaml]"):
        raw = path.read_text()
        yaml = safe_load(raw)
        acc.update(yaml)

    forwards: Forwards = decode(Forwards, acc)
    fwds: MutableMapping[str, MutableSet[Mapping[str, Union[str, int]]]] = {}
    for hostname, fws in forwards.items():
        specs = fwds.setdefault(hostname, set())
        for fw in fws:
            spec = {
                "PROTO": fw.proto,
                "FROM_PORT": fw.from_port,
                "TO_PORT": fw.to_port,
                "PROXY_PROTO": fw.proxy_proto,
            }
            specs.add(spec)
    return fwds
