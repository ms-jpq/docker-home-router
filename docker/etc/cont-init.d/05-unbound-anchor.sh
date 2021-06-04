#!/usr/bin/env bash

set -u


TMP_KEY='/var/tmp/unbound-root.key'
DEST_KEY='/data/unbound/root.key'
ARGS=(
  -a "$DEST_KEY"
  )


if [[ -f "$TMP_KEY" ]] && [[ ! -f "$DEST_KEY" ]]
then
if ! mv -- "$TMP_KEY" "$DEST_KEY"
then
  exit 1
fi
fi

chown "$USER:$USER" -- "$DEST_KEY"
s6-setuidgid "$USER" unbound-anchor "${ARGS[@]}"
true

