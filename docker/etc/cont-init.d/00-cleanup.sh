#!/usr/bin/env bash

set -eu
set -o pipefail
shopt -s globstar nullglob


ARGS=(
  /tmp/*
  /srv/run/nftables/docker/*
  )


exec rm -rf -- "${ARGS[@]}"
