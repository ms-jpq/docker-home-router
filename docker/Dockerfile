FROM ubuntu:focal


ARG S6="https://github.com/just-containers/s6-overlay/releases/download/v2.2.0.3/s6-overlay-amd64-installer"


RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
    nftables \
    curl \
    wget \
    net-tools \
    iproute2 \
    python3-pip \
    dnsmasq \
    unbound \
    unbound-anchor \
    avahi-daemon \
    chrony \
    tor \
    squid \
    squidclient \
    wireguard \
    qrencode && \
    rm -rf /var/lib/apt/lists/* /tmp/*


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
    pip3 install --upgrade /code && \
    rm -rf /code && \
    unbound-anchor -a /srv/run/unbound/root.key && exit 1 || exit 0


### Well known
# 53    TCP/UDP -> DNS
# 67    UDP     -> DHCPv4
# 123   UDP     -> NTP
# 547   UDP     -> DHCPv6
# 5353  UDP     -> Bonjour

### Configurable
# 8888  TCP     -> HTTP - Statistics
# 9060  TCP     -> TOR
# 9080  TCP     -> Squid
# 51820 UDP     -> WireGuard
EXPOSE 53/tcp 53/udp \
       67/udp \
       123/udp \
       5353/udp \
       8888/tcp \
       9060/tcp \
       9080/tcp \
       51820/udp


# WAN_IF, LAN_IF           -> Interface names: assigned different IP address space
# GUEST_IF                 -> Optional: see above
# WG_IF                    -> Name for wireguard interface
# IF_EXCLUSIONS            -> ',' delimited : Interface IPv4 addrs with these GLOB patterns will be excluded
# IP6_ULA_GLOBAL           -> Globally unique 40 bit prefix (in HEX)
# IP6_ULA_SUBNET_EXCLUSION -> ',' delimited : Organizationally unique 16 bit prefix (in HEX)
# IP4_EXCLUSION            -> ',' delimited : Networks to exclude from assignment in 'x.x.x.x/mask' form
# DNS_SERVERS              -> Upstream DNS servers: default is systemd-resolve
# NTP_SERVERS              -> Upstream NTP servers
# WG_PEERS                 -> ',' delimited : List of peers to create for wireguard
# STATS_PORT               -> Port for statistics
# SERVER_NAME              -> Name of router
ENV WAN_IF= \
    LAN_IF= \
    WG_IF=wg0 \
    GUEST_IF= \
    IF_EXCLUSIONS=docker* \
    LOOPBACK_EXCLUSION=127.0.0.0/16 \
    IP6_ULA_GLOBAL= \
    IP6_ULA_SUBNET_EXCLUSION= \
    IP4_EXCLUSION=10.0.0.0/20,192.168.0.0/20,172.16.0.0/20 \
    IP4_PREFIX=22 \
    LEASE_TIME=2 \
    DNS_SERVERS= \
    NTP_SERVERS=0.ca.pool.ntp.org,1.ca.pool.ntp.org,2.ca.pool.ntp.org,3.ca.pool.ntp.org \
    WG_PEERS="me,my wife,my wife's boyfriend" \
    WAN_DOMAIN= \
    LAN_DOMAIN=lan \
    STATS_PORT=8888 \
    TOR_PORT=9060 \
    SQUID_PORT=9080 \
    WG_PORT=51820


VOLUME /config \
       /data
