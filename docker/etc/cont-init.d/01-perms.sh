#!/usr/bin/env bash

set -eu
set -o pipefail


ARGS=(
  /srv
  /config
  /data
  )


exec chown -R "$USER:$USER" -- "${ARGS[@]}"
