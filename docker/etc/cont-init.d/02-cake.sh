#!/usr/bin/env bash

set -eu
set -o pipefail


exec s6-setuidgid "$USER" python3 -m router.cake
