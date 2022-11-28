#!/usr/bin/env bash

set -Eeu
set -o pipefail


cd "$(dirname "$0")" || exit 1


exec unbound-control -c "$PWD/0-include.conf" "$@"
