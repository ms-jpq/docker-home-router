#!/usr/bin/env bash

set -eu
set -o pipefail


exec chown -R router:router /code /srv
