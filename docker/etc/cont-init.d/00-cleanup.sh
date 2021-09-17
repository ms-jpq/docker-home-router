#!/usr/bin/env bash

set -eu
set -o pipefail
shopt -s globstar nullglob


ARGS=(
  /tmp/*
  )


exec rm -rf -- "${ARGS[@]}"
