#!/usr/bin/env bash

set -eu
set -o pipefail


exec /venv/bin/python3 -m router ifup "$@"
