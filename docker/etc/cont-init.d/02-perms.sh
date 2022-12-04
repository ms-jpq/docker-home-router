#!/usr/bin/env bash

set -Eeu
set -o pipefail
shopt -s globstar nullglob
export PATH="/usr/sbin:$PATH"


TFTP_SRC=/config/tftp
NFT_DEST=/srv/run/nftables/user/
NTP_DEST=/srv/run/chrony/sources.d/

mkdir -p -- "$NFT_DEST" "$NTP_DEST"


NFTS=(/config/nftables/*)
NTPS=(/config/ntpsources/*)

if (( ${#NFTS[@]} ))
then
  cp -r -- "${NFTS[@]}" "$NFT_DEST"
fi

if (( ${#NTPS[@]} ))
then
  cp -r -- "${NTPS[@]}" "$NTP_DEST"
fi


if [[ -d "$TFTP_SRC" ]]
then
  ln -s -f -- "$TFTP_SRC" /srv/run/tftp
fi

exec chown -R -- "$USER:$USER" /srv /data
