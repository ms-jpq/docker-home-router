#!/usr/bin/env bash

set -eu
set -o pipefail
export PATH="/usr/sbin:$PATH"


cd "$(dirname "$0")" || exit 1


nft --file - < ./0-flush.conf
printf '%s\n' 'NFT SUCC'
