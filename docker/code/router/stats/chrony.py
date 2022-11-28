from os import linesep
from subprocess import check_output


def feed() -> str:
    raw_1 = check_output(("chronyc", "tracking"), text=True)
    raw_2 = check_output(("chronyc", "serverstats"), text=True)
    return f"{raw_1}{linesep * 3}{raw_2}"
