FROM ubuntu:focal


ARG S6="https://github.com/just-containers/s6-overlay/releases/download/v2.2.0.1/s6-overlay-amd64-installer"


RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
    nftables \
    curl \
    wget \
    net-tools \
    iproute2 \
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
ENV S6_KEEP_ENV=1 \
    S6_BEHAVIOUR_IF_STAGE2_FAILS=2
ENTRYPOINT ["/init"]


WORKDIR /srv/run
COPY . /
ENV USER=router
RUN useradd --user-group --shell=/usr/sbin/nologin "$USER" && \
    pip3 install --upgrade /code


# 53    TCP/UDP -> DNS
# 67    UDP     -> DHCP
# 123   UDP     -> NTP
# 500   UDP     -> L2TP
# 1080  TCP     -> TOR PROXY
# 4500  UDP     -> L2TP
# 5335  TCP/UDP -> DNS2
# 8080  TCP     -> HTTP ALT
# 51820 UDP     -> WIREGUARD
EXPOSE 53/tcp 53/udp \
       67/udp \
       123/udp \
       500/udp \
       1080/tcp \
       4500/udp \
       5335/tcp 5335/udp \
       8080/tcp \
       51820/udp


# WAN_IF, LAN_IF           -> Interface names: assigned different IP address space
# GUEST_IF                 -> Optional: see above
# WG_IF                    -> Name for wireguard interface
# IP6_ULA_GLOBAL           -> Globally unique 40 bit prefix (in HEX)
# IP6_ULA_SUBNET_EXCLUSION -> ',' delimited : Organizationally unique 16 bit prefix (in HEX)
# IP4_EXCLUSION            -> ',' delimited : Networks to exclude from assignment in 'x.x.x.x/mask' form
# DNS_SERVERS              -> Upstream DNS servers: default is unbound recursive resolver
# NTP_SERVERS              -> Upstream NTP servers
# WG_PEERS                 -> ',' delimited : List of peers to create for wireguard
ENV WAN_IF= \
    LAN_IF= \
    WG_IF=wg0 \
    GUEST_IF= \
    IP6_ULA_GLOBAL= \
    IP6_ULA_SUBNET_EXCLUSION= \
    IP4_EXCLUSION=10.0.0.0/24,192.168.0.0/24,172.16.0.0/24 \
    DNS_SERVERS=127.0.0.1#5335,::1#5335 \
    NTP_SERVERS=0.ca.pool.ntp.org,1.ca.pool.ntp.org,2.ca.pool.ntp.org,3.ca.pool.ntp.org \
    WG_PEERS="wife,wife's boyfriend" \
    SERVER_NAME=

