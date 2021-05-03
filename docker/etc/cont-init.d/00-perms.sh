#!/usr/bin/env bash

set -eu
set -o pipefail


ARGS=(
  /srv
  /config
  /data
  /var/log/squid
  )


exec chown -R "$USER:$USER" "${ARGS[@]}"
