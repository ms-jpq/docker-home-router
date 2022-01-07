from datetime import datetime, timedelta
from subprocess import check_output, run
from time import sleep
from typing import Optional

from ..consts import DATA, SHORT_DURATION, UNBOUND_CTL

_MAX_DELTA = timedelta(seconds=30)

_UNBOUND = DATA / "unbound"
_CACHE = _UNBOUND / "cache.txt"
_TMP = _UNBOUND / ".cache.txt"


def _cached() -> Optional[bytes]:
    _CACHE.parent.mkdir(parents=True, exist_ok=True)
    if not _CACHE.exists():
        return None
    else:
        mtime = _CACHE.stat().st_mtime
        mod = datetime.utcfromtimestamp(mtime)
        now = datetime.utcnow()
        if abs(now - mod) > _MAX_DELTA:
            return None
        else:
            return _CACHE.read_bytes()


def main() -> None:
    if cached := _cached():
        run(
            (UNBOUND_CTL, "load_cache"), input=cached, timeout=SHORT_DURATION
        ).check_returncode()

    while True:
        raw = check_output((UNBOUND_CTL, "dump_cache"), timeout=SHORT_DURATION)
        _TMP.write_bytes(raw)
        _TMP.replace(_CACHE)
        sleep(60)
