#!/usr/bin/env bash

set -eu
set -o pipefail
shopt -s globstar nullglob


ARGS=(
  /srv
  /data
  )


RULES=(/config/nftables/*)

if (( ${#RULES[@]} ))
then
  cp -r -- "${RULES[@]}" /srv/run/nftables/user/
fi

exec chown -R "$USER:$USER" -- "${ARGS[@]}"
