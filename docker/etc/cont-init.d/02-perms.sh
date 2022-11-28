#!/usr/bin/env bash

set -Eeu
set -o pipefail
shopt -s globstar nullglob
export PATH="/usr/sbin:$PATH"


ARGS=(
  /srv
  /data
  )



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

exec chown -R "$USER:$USER" -- "${ARGS[@]}"
