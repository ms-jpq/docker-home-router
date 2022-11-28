#!/usr/bin/env bash

set -Eeu
set -o pipefail
shopt -s globstar nullglob
export PATH="/usr/sbin:$PATH"


ARGS=(
  /tmp/*
  /srv/run/nftables
  )


exec rm -rf -- "${ARGS[@]}"
