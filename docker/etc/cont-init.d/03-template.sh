#!/usr/bin/env bash

set -Eeu
set -o pipefail
export PATH="/usr/local/bin:$PATH"


s6-setuidgid "$USER" /venv/bin/python3 -m router template
exec -- chown -R -- root:root /srv/run/sudo
