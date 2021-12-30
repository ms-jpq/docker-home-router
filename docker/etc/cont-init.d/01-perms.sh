#!/usr/bin/env bash

set -eu
set -o pipefail
shopt -s globstar nullglob


ARGS=(
  /srv
  /data
  )


if [[ -f /config/nftables ]]
then
  cp -r -- /config/nftables /srv/run/nftables/user
fi

exec chown -R "$USER:$USER" -- "${ARGS[@]}"
