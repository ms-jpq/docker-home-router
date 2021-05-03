#!/usr/bin/env bash

set -eu
set -o pipefail


ARGS=(
  /tmp/*
  )


exec rm -rf -- "${ARGS[@]}"
