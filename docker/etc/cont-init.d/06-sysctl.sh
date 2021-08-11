#!/usr/bin/env bash

set -eu
set -o pipefail


sysctl net.ipv4.ip_forward=1 || true
sysctl net.ipv6.conf.all.forwarding=1 || true
