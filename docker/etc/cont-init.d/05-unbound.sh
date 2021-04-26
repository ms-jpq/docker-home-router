#!/usr/bin/env bash

set -eu
set -o pipefail

UNBOUND='/data/unbound'

ARGS=(
  -a "$UNBOUND/root.key"
  )


mkdir -p "$UNBOUND"
exec s6-setuidgid "$USER" unbound-anchor "${ARGS[@]}"
