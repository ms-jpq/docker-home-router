#!/usr/bin/env bash

set -eu
set -o pipefail


ARGS=(
  /srv
  /config
  /data
  /var/run/unbound
  /var/log/chrony
  )


exec chown -R "$USER:$USER" "${ARGS[@]}"
