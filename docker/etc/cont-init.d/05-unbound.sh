#!/usr/bin/env bash

set -eu
set -o pipefail


UNBOUND='/data/unbound'

ARGS=(
  -a "$UNBOUND/root.key"
  )


s6-setuidgid "$USER" mkdir -p "$UNBOUND"
exec s6-setuidgid "$USER" unbound-anchor "${ARGS[@]}"
