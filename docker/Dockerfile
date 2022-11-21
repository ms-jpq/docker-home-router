FROM ubuntu:jammy


ARG S6_OVERLAY_VERSION=3.0.0.2-2
SHELL ["/bin/bash", "-Eeu", "-o", "pipefail", "-c"]


RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install --yes --no-install-recommends -- \
    sudo \
    curl \
    software-properties-common \
    gpg-agent \
    isc-dhcp-client \
    neovim \
    procps \
    nftables \
    openssl \
    iproute2 \
    python3-venv \
    dnsmasq \
    unbound \
    avahi-daemon \
    chrony \
    tor \
    squid \
    squidclient \
    wireguard \
    qrencode \
    iftop \
    nginx && \
    rm -rf -- /tmp/*


RUN curl --location --output /tmp/s6-overlay-noarch.tar.xz -- \
    https://github.com/just-containers/s6-overlay/releases/download/v"$S6_OVERLAY_VERSION"/s6-overlay-noarch-"$S6_OVERLAY_VERSION".tar.xz && \
    curl --location --output /tmp/s6-overlay-some-arch.tar.xz -- \
    https://github.com/just-containers/s6-overlay/releases/download/v"$S6_OVERLAY_VERSION"/s6-overlay-"$(arch)"-"$S6_OVERLAY_VERSION".tar.xz && \
    tar -C / -Jxpf /tmp/s6-overlay-noarch.tar.xz && \
    tar -C / -Jxpf /tmp/s6-overlay-some-arch.tar.xz && \
    rm -rf -- /tmp/**
ENV S6_KEEP_ENV=1 \
    S6_BEHAVIOUR_IF_STAGE2_FAILS=2 \
    S6_CMD_WAIT_FOR_SERVICES_MAXTIME=0 \
    S6_SERVICES_GRACETIME=0 \
    S6_KILL_GRACETIME=0
ENTRYPOINT [ "/init" ]




WORKDIR /srv/run
COPY . /
ENV USER=router
RUN useradd --user-group --shell=/usr/sbin/nologin -- "$USER" && \
    python3 -m venv -- /venv && \
    /venv/bin/pip3 install --upgrade --no-cache-dir -- /code && \
    rm -rf -- /etc/dnsmasq* /code

### Well known
# 53    TCP/UDP -> DNS
# 67    UDP     -> DHCPv4
# 123   UDP     -> NTP
# 547   UDP     -> DHCPv6
# 853   TCP     -> DNS-TLS
# 5353  UDP     -> Bonjour

# 51820 UDP     -> WireGuard
# 8080  TCP     -> HTTP alt
# 3128  TCP     -> Squid
# 1080  TCP     -> Tor
EXPOSE 53/tcp 53/udp \
    67/udp \
    123/udp \
    547/udp \
    853/tcp \
    5353/udp \
    51820/udp \
    8080/tcp \
    3128/tcp \
    1080/tcp


VOLUME /config \
    /data
