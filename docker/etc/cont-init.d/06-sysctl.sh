#!/usr/bin/env bash

set -eu
set -o pipefail


ARGS=(
  net.ipv4.ip_forward=1
  net.ipv6.conf.all.forwarding=1
  net.ipv4.tcp_congestion_control=bbr
  )


for arg in "${ARGS[@]}"
do
  sysctl "$arg" || true
done
