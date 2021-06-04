from datetime import datetime, timedelta
from subprocess import CalledProcessError, check_call, check_output, run
from time import sleep

from ..consts import DATA, SHORT_DURATION, UNBOUND_CTL

_MAX_DELTA = timedelta(minutes=1)

_UNBOUND = DATA / "unbound"
_CACHE = _UNBOUND / "cache.txt"
_TMP = _UNBOUND / ".cache.txt"


def _cached() -> bytes:
    _CACHE.parent.mkdir(parents=True, exist_ok=True)
    if not _CACHE.exists():
        return bytes()
    else:
        mtime = _CACHE.stat().st_mtime
        mod = datetime.utcfromtimestamp(mtime)
        now = datetime.utcnow()
        if abs(now - mod) > _MAX_DELTA:
            return bytes()
        else:
            return _CACHE.read_bytes()


def _wait() -> None:
    while True:
        try:
            check_call((str(UNBOUND_CTL), "status"), timeout=SHORT_DURATION)
        except CalledProcessError:
            pass
        else:
            break


def main() -> None:
    cached = _cached()

    _wait()
    if cached:
        run(
            (str(UNBOUND_CTL), "load_cache"), input=cached, timeout=SHORT_DURATION
        ).check_returncode()

    while True:
        raw = check_output((str(UNBOUND_CTL), "dump_cache"), timeout=SHORT_DURATION)
        _TMP.write_bytes(raw)
        _TMP.replace(_CACHE)
        sleep(60)
