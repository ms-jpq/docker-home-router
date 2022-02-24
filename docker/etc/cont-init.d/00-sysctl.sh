#!/usr/bin/env bash

set -eu
set -o pipefail
export PATH="/usr/sbin:$PATH"


ARGS=(
  net.ipv4.ip_forward=1
  net.ipv6.conf.all.forwarding=1
  net.ipv4.tcp_congestion_control=bbr
  net.ipv6.conf.all.accept_dad=0
  # TODO -- replace with net.ipv6.conf.all.optimistic_dad = 1
  )


for arg in "${ARGS[@]}"
do
  sysctl "$arg" || true
done
