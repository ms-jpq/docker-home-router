#!/usr/bin/env bash

set -eu
set -o pipefail
shopt -s globstar nullglob


ARGS=(
  /srv
  /var/run/chrony
  /data
  )


RULES=(/config/nftables/*)
DEST=/srv/run/nftables/user/

if (( ${#RULES[@]} ))
then
  mkdir -p -- "$DEST"
  cp -r -- "${RULES[@]}" "$DEST"
fi

exec chown -R "$USER:$USER" -- "${ARGS[@]}"
