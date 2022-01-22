#!/usr/bin/env bash

set -eu
set -o pipefail


cd "$(dirname "$0")" || exit 1


SCRIPT="$(
cat << EOF
flush ruleset

include "./sys/*.conf";
include "./user/*.conf";
EOF
)"


exec nft --file - <<< "$SCRIPT"
