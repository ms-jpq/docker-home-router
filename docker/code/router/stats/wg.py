from subprocess import check_output

from ..consts import SHORT_DURATION


def feed() -> str:
    raw = check_output(
        ("sudo", "--non-interactive", "--", "wg", "show"),
        text=True,
        timeout=SHORT_DURATION,
    )
    return raw.strip().expandtabs()
