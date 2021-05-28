from subprocess import CalledProcessError, check_call, check_output, run
from time import sleep

from ..consts import DATA, RUN, SHORT_DURATION, UNBOUND_CTL

_CACHE = DATA / "unbound" / "cache.txt"
_TMP = RUN / "unbound" / "cache.txt"


def _wait() -> None:
    while True:
        try:
            check_call((str(UNBOUND_CTL), "status"), timeout=SHORT_DURATION)
        except CalledProcessError:
            pass
        else:
            break


def main() -> None:
    _CACHE.touch()
    cached = _CACHE.read_bytes()
    _CACHE.unlink(missing_ok=True)

    _wait()
    run(
        (str(UNBOUND_CTL), "load_cache"), input=cached, timeout=SHORT_DURATION
    ).check_returncode()

    while True:
        raw = check_output((str(UNBOUND_CTL), "dump_cache"), timeout=SHORT_DURATION)
        _TMP.write_bytes(raw)
        _TMP.replace(_CACHE)
        sleep(60)
