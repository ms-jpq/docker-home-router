from os import sep
from pathlib import Path
from subprocess import CalledProcessError, check_call, check_output, run
from tempfile import gettempdir
from time import sleep

from ..consts import UNBOUND_CTL

_CACHE = Path(sep, "data", "unbound-cache.txt")
_TMP = Path(gettempdir()) / "unbound-cache.txt"


def _wait() -> None:
    while True:
        try:
            check_call((str(UNBOUND_CTL), "status"))
        except CalledProcessError:
            pass
        else:
            break


def main() -> None:
    _CACHE.touch()
    cached = _CACHE.read_bytes()
    _CACHE.unlink(missing_ok=True)

    _wait()
    run((str(UNBOUND_CTL), "load_cache"), input=cached).check_returncode()

    while True:
        raw = check_output((str(UNBOUND_CTL), "dump_cache"))
        _TMP.write_bytes(raw)
        _TMP.replace(_CACHE)
        sleep(60)
