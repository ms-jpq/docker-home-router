#!/usr/bin/env bash

set -eu
set -o pipefail
export PATH="/usr/local/bin:$PATH"


s6-setuidgid "$USER" /venv/bin/python3 -m router template
exec chown -R root:root -- /srv/run/sudo
