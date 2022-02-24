#!/usr/bin/env bash

set -eu
set -o pipefail


s6-setuidgid "$USER" /venv/bin/python3 -m router template
exec chown -R root:root -- /srv/run/sudo
