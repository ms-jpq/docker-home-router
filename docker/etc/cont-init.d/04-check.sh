#!/usr/bin/env bash

set -eu
set -o pipefail


exec nft --file /data/nftables/0-main.conf --check
