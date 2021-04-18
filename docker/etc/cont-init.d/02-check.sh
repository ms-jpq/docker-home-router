#!/usr/bin/env bash

set -eu
set -o pipefail


exec s6-setuidgid "$USER" nftables --file /nftables/0-main.conf --check
