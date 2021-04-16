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


ADD --chmod=+x https://github.com/just-containers/s6-overlay/releases/download/v2.2.0.1/s6-overlay-amd64-installer /tmp/
RUN /tmp/s6-overlay-amd64-installer /
ENTRYPOINT ["/init"]


EXPOSE 8080
