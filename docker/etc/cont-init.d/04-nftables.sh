#!/usr/bin/env bash

set -eu
set -o pipefail


exec /srv/run/nftables/nft.sh
