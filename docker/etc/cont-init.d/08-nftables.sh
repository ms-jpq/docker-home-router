#!/usr/bin/env bash

set -Eeu
set -o pipefail
export PATH="/usr/sbin:$PATH"


exec -- /srv/run/nftables/nft.sh
