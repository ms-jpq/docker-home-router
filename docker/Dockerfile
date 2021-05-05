FROM ubuntu:focal


ARG S6="https://github.com/just-containers/s6-overlay/releases/download/v2.2.0.3/s6-overlay-amd64-installer"


RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
    nftables \
    wget \
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


# WAN_IF, LAN_IF           -> [REQUIRED] Interface names: assigned different IP address space
# GUEST_IF                 -> see above, but not required
# WG_IF                    -> Name for wireguard interface
# IF_EXCLUSIONS            -> ',' delimited : For interfaces with these glob patterns, their IPv4 networks will be excluded from subnet calculations

# LOOPBACK_EXCLUSION       -> ',' delimited : IPv4 loopback addresses excluded from assignment
# IP6_ULA_GLOBAL           -> Globally unique 40 bit prefix (in HEX)
# IP6_ULA_SUBNET_EXCLUSION -> ',' delimited : Organizationally unique 16 bit prefix (in HEX)
# IP4_EXCLUSION            -> ',' delimited : Networks to exclude from assignment in 'x.x.x.x/mask' form
# IP4_PREFIX               -> ',' delimited : Prefix of IPv4 networks

# DHCP_LEASE_TIME          -> DHCP lease duration in hours, min is 2
# DNS_SERVERS              -> Upstream DNS servers: default is a recursive resolver @ loopback
# LAN_DOMAIN               -> Domain name of local networks

# WG_DOMAIN                -> IP / domain name of wireguard server location
# WG_PEERS                 -> ',' delimited : List of peers to create for wireguard
# WG_PORT                  -> Port for wireguard server

# STATS_PORT               -> Port for statistics
# TOR_PORT                 -> Port for TOR portal
# SQUID_PORT               -> Port for Squid proxy

ENV WAN_IF= \
    LAN_IF= \
    WG_IF=wg0 \
    GUEST_IF= \
    IF_EXCLUSIONS=docker* \
    LOOPBACK_EXCLUSION=127.0.0.0/16 \
    IP6_ULA_GLOBAL= \
    IP6_ULA_SUBNET_EXCLUSION= \
    IP4_EXCLUSION=10.0.0.0/20,192.168.0.0/20,172.16.0.0/20 \
    IP4_PREFIX=24 \
    DHCP_LEASE_TIME=2 \
    DNS_SERVERS= \
    LAN_DOMAIN=lan \
    WG_DOMAIN= \
    WG_PEERS="me,my wife,my wife's boyfriend" \
    WG_PORT=51820 \
    STATS_PORT=8888 \
    TOR_PORT=9060 \
    SQUID_PORT=9080


VOLUME /config \
       /data
