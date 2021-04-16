ARG S6="https://github.com/just-containers/s6-overlay/releases/download/v2.2.0.1/s6-overlay-amd64-installer"
FROM ubuntu:focal


RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
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


ADD --chmod=+x  "$S6" /tmp/s6
RUN /tmp/s6 /
ENTRYPOINT ["/init"]


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
# IP6_ULA_PREFIX -> Globally unique 40 bit prefix (in HEX)
# IP4_EXCLUSION  -> Networks to exclude from pool calculations
ENV WAN_IF= \
    LAN_IF= \
    GUEST_IF= \
    IP6_ULA_PREFIX= \
    IP4_EXCLUSION=
