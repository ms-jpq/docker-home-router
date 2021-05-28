#!/usr/bin/env bash

set -eu
set -o pipefail


CACHE='/data/unbound-cache.txt'
TMP="$(mktemp)"


s6-setuidgid "$USER" /srv/run/unbound/ctl.sh dump_cache > "$TMP"
s6-setuidgid "$USER" mv -- "$TMP" "$CACHE"
