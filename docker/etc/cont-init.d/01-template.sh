#!/usr/bin/env bash

set -eu
set -o pipefail


mkdir -p /data/stream.d
exec s6-setuidgid "$USER" python3 -m router template
