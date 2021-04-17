FROM ubuntu:focal


ARG S6="https://github.com/just-containers/s6-overlay/releases/download/v2.2.0.1/s6-overlay-amd64-installer"


RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
    wget \
    python3-pip \
    nginx \
    dnsmasq \
    unbound \
    chrony \
    tor \
    wireguard \
    qrencode \
    rclone \
    strongswan \
    strongswan-pki \
    libcharon-extra-plugins \
    libcharon-extauth-plugins \
    libstrongswan-extra-plugins && \
    rm -rf /var/lib/apt/lists/*


RUN wget "${S6}" --output-document /tmp/s6 && \
    chmod +x /tmp/s6 && \
    /tmp/s6 / && \
    rm -rf /tmp/*
ENTRYPOINT ["/init"]


COPY . /
RUN useradd --user-group --shell=/usr/sbin/nologin router && \
    pip3 install --upgrade /code


# 53    TCP/UDP -> DNS
# 67    UDP     -> DHCP
# 80    TCP     -> HTTP
# 123   UDP     -> NTP
# 500   UDP     -> L2TP
# 1080  TCP     -> TOR PROXY
# 4500  UDP     -> L2TP
# 5335  TCP/UDP -> DNS2
# 51820 UDP     -> WIREGUARD
EXPOSE 53/tcp 53/udp \
       67/udp \
       80/tcp \
       123/udp \
       500/udp \
       1080/tcp \
       4500/udp \
       5335/tcp 5335/udp \
       51820/udp


# WAN_IF, LAN_IF -> Interface names: assigned different IP address space
# GUEST_IF       -> Optional: see above
# IP6_ULA_RAND   -> Globally unique 40 bit prefix (in HEX)
# IP6_ULA_SUBNET -> Organizationally unique 16 bit prefix (in HEX)
# IP4_EXCLUSION  -> ',' delimited : Networks to exclude from assignment in 'x.x.x.x/mask' form
# DNS            -> Upstream DNS servers: default is unbound recursive resolver
ENV WAN_IF= \
    LAN_IF= \
    GUEST_IF= \
    IP6_ULA_RAND= \
    IP6_ULA_SUBNET= \
    IP4_EXCLUSION=10.0.0.0/24,192.168.0.0/24,172.16.0.0/24 \
    DNS=127.0.0.1:5335,[0:0:0:0:0:0:0:1]:5335
