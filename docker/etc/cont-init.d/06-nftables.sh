#!/usr/bin/env bash

set -eu
set -o pipefail


export PATH="/usr/sbin:$PATH"
exec /srv/run/nftables/nft.sh
