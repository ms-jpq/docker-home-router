#!/usr/bin/env bash

set -eu
set -o pipefail


cd /data/nftables || exit 1


CHECK='include "./*.conf"'
exec nft --file - --check <<< "$CHECK"
