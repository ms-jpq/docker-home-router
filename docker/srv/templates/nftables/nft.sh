#!/usr/bin/env bash

set -eu
set -o pipefail


SCRIPT="$(
cat << EOF
flush ruleset

include "./docker/*.conf";
include "./user/*.conf";
EOF
)"


exec nft --file - <<< "$SCRIPT"
