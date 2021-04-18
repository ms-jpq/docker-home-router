#!/usr/bin/env bash

set -eu
set -o pipefail


ARGS=(
  /srv
  /data
  /root/.rclone.conf
  )


exec chown -R "$USER:$USER" "${ARGS[@]}"
