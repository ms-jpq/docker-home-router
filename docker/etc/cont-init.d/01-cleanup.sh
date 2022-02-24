#!/usr/bin/env bash

set -eu
set -o pipefail
shopt -s globstar nullglob
export PATH="/usr/sbin:$PATH"


ARGS=(
  /tmp/*
  /srv/run/nftables
  )


exec rm -rf -- "${ARGS[@]}"
