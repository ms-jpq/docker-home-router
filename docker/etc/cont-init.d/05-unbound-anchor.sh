#!/usr/bin/env bash

set -eu
set -o pipefail


TMP_KEY='/var/tmp/unbound-root.key'
DEST_KEY='/data/unbound/root.key'
ARGS=(
  -a "$DEST_KEY"
  )


if [[ ! -f "$DEST_KEY" ]]
then
  cp -- "$TMP_KEY" "$DEST_KEY"
fi

chown "$USER:$USER" -- "$DEST_KEY"
s6-setuidgid "$USER" unbound-anchor "${ARGS[@]}" || true
