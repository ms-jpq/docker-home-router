#!/usr/bin/env bash

set -eu
set -o pipefail


exec exec python3 -m router dh_script "$@"
