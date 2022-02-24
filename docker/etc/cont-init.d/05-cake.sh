#!/usr/bin/env bash

set -eu
set -o pipefail
export PATH="/usr/sbin:$PATH"


exec /venv/bin/python3 -m router cake
