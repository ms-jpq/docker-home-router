#!/usr/bin/env bash

set -Eeu
set -o pipefail
export PATH="/usr/sbin:$PATH"


exec -- /venv/bin/python3 -m router cake
