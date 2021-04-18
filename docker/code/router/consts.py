from pathlib import Path

LFS = ","

_SRV = Path("/", "srv")

TEMPLATES = _SRV / Path("templates")
RUN = _SRV / Path("run")

NETWORKS = RUN / "networks.json"
