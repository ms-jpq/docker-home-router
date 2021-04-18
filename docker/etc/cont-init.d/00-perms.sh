#!/usr/bin/env bash

set -eu
set -o pipefail


exec chown -R "$USER:$USER" /code /srv
