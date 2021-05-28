#!/usr/bin/env bash

set -eu
set -o pipefail


CACHE='/data/unbound-cache.txt'
TMP="$(s6-setuidgid "$USER" mktemp)"


s6-setuidgid "$USER" /srv/run/unbound/ctl.sh dump_cache > "$TMP"
exec s6-setuidgid "$USER" mv -- "$TMP" "$CACHE"
