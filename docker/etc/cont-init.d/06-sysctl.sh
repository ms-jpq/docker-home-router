#!/usr/bin/env bash

set -u


sysctl net.ipv4.ip_forward=1
sysctl net.ipv6.conf.all.forwarding=1

