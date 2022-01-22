FROM ubuntu:jammy


ARG S6="https://github.com/just-containers/s6-overlay/releases/download/v2.2.0.3/s6-overlay-amd64-installer"


RUN apt update && \
    DEBIAN_FRONTEND=noninteractive apt install --yes --no-install-recommends -- \
    sudo \
    software-properties-common \
    gpg-agent \
    neovim \
    procps \
    nftables \
    openssl \
    wget \
    iproute2 \
    python3-venv \
    wide-dhcpv6-client \
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


# RUN printf '%s' \
#     "deb https://pkg.cloudflare.com/ $(cat /etc/lsb-release | grep -e 'DISTRIB_CODENAME' | awk -F '=' '{print $2}') main" | \
#     tee /etc/apt/sources.list.d/cloudflare.list && \
#     wget --output-document - -- https://pkg.cloudflare.com/cloudflare-main.gpg | apt-key add -
    # TODO -- install cloudflard
    # https://github.com/AdguardTeam/dnsproxy


RUN wget --output-document /tmp/s6 -- "${S6}" && \
    chmod +x -- /tmp/s6 && \
    /tmp/s6 / && \
    rm -rf -- /etc/s6/services/s6-fdholderd/down /tmp/*
ENV S6_KEEP_ENV=1 \
    S6_BEHAVIOUR_IF_STAGE2_FAILS=2
ENTRYPOINT ["/init"]


RUN python3 -m venv -- /venv
ENV PATH="/venv/bin:$PATH"


WORKDIR /srv/run
COPY . /
ENV USER=router
RUN useradd --user-group --shell=/usr/sbin/nologin -- "$USER" && \
    pip3 install --upgrade --no-cache-dir -- /code && \
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
