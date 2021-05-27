#!/usr/bin/env bash

set -u


ARGS=(
  -a /srv/run/unbound/root.key
  )


exec s6-setuidgid "$USER" unbound-anchor "${ARGS[@]}"

