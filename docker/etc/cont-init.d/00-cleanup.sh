#!/usr/bin/env bash

set -eu
set -o pipefail
shopt -s globstar nullglob


ARGS=(
  /tmp/*
  /srv/run/nftables
  )


exec rm -rf -- "${ARGS[@]}"
