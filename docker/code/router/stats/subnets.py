from json import dumps
from subprocess import check_output

from std2.pickle.encoder import new_encoder

from ..consts import SHORT_DURATION
from ..subnets import Networks, load_networks


def feed() -> str:
    networks = load_networks()
    data = new_encoder[Networks](Networks)(networks)
    json = dumps(data, check_circular=False, ensure_ascii=False)
    yaml = check_output(
        ("sortd", "yaml"), text=True, input=json, timeout=SHORT_DURATION
    )
    return yaml.strip()
