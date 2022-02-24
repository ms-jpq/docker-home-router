#!/usr/bin/env bash

set -eu
set -o pipefail
export PATH="/usr/sbin:$PATH"


cd "$(dirname "$0")" || exit 1


SCRIPT="$(
cat << EOF
flush ruleset

include "./sys/*.conf";
include "./user/*.conf";
EOF
)"


nft --file - <<< "$SCRIPT"
printf '%s\n' 'NFT SUCC'
