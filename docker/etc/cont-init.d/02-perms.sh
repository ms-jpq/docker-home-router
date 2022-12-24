#!/usr/bin/env bash

set -Eeu
set -o pipefail
shopt -s globstar nullglob
export PATH="/usr/sbin:$PATH"


TFTP_SRC=/config/tftp
TFTP_DST=/tftp
NFT_DST=/srv/run/nftables/user/
NTP_DST=/srv/run/chrony/sources.d/
DHCPD_DST=/srv/run/dnsmasq/dhcp/dhcp-optsdir/


mkdir -p -- "$NFT_DST" "$NTP_DST" "$DHCPD_DST"


NFTS=(/config/nftables/*)
NTPS=(/config/ntpsources/*)
DHCPDS=(/config/dhcpd/*)

if (( ${#NFTS[@]} ))
then
  cp -r -- "${NFTS[@]}" "$NFT_DST"
fi

if (( ${#NTPS[@]} ))
then
  cp -r -- "${NTPS[@]}" "$NTP_DST"
fi

if (( ${#DHCPDS[@]} ))
then
  cp -r -- "${DHCPDS[@]}" "$DHCPD_DST"
fi

if [[ -d "$TFTP_SRC" ]]
then
  rm -fr -- "$TFTP_DST"
  ln -s -f -- "$TFTP_SRC" "$TFTP_DST"
fi

exec -- chown -R -- "$USER:$USER" /srv /data
