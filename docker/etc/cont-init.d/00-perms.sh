#!/usr/bin/env bash

set -eu
set -o pipefail


ARGS=(
  /srv
  /data
  /var/run/unbound
  /var/run/dnsmasq/leases
  /var/log/chrony
  )


exec chown -R "$USER:$USER" "${ARGS[@]}"
