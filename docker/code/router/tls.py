from .consts import DATA

_PEM = DATA / "unbound" / "tls.pem"
_KEY = DATA / "unbound" / "tls.key"


def gen() -> None:
    if not _PEM.exists():
        pass
    if not _KEY.exists():
        pass
