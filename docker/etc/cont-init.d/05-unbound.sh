#!/usr/bin/env bash

set -eu
set -o pipefail


ARGS=(
  -a /data/unbound/root.key
  )


exec s6-setuidgid "$USER" unbound-anchor "${ARGS[@]}"
