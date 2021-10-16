#!/usr/bin/env bash

set -eu
set -o pipefail


s6-setuidgid "$USER" python3 -m router template
chown -R root:root -- /srv/run/sudo
