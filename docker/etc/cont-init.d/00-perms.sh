#!/usr/bin/env bash

set -eu
set -o pipefail


ARGS=(
  /srv
  /config
  /data
  /var/log/squid
  /tmp/unbound-root.key
  )


exec chown -R "$USER:$USER" "${ARGS[@]}"
