#!/usr/bin/env bash

set -eu
set -o pipefail


CHECK='include "/data/nftables/*.conf";'
exec nft --file - --check <<< "$CHECK"
