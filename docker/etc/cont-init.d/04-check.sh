#!/usr/bin/env bash

set -eu
set -o pipefail


nft --file /data/nftables/0-main.conf --check
