# Install.md

## Step 0.

If you are not happy and want to cleanly uninstall everything.

```sh
rm /etc/sysctl.d/50-ip-fwd.conf  # disable ip6 forwarding
apt purge nftables               # remove firewall
docker rm -f <name of container> # remove docker container
```

## Step 1. Stuff you can't do with Docker alone

```sh
# This enable ip6 forwarding
# Docker already enabled ip4 forwarding, so you dont need to do it again
echo 'net.ipv6.conf.all.forwarding=1' > /etc/sysctl.d/50-ip-fwd.conf

# Install firewall
# Firewall cannot be entirely inside Docker, because Docker starts after network
apt install nftables
systemctl enable nftables
```

Add [`nftables.conf`](https://github.com/ms-jpq/docker-home-router/tree/whale/install/nftables.conf) to `/etc/nftables.conf`

This is a very basic & restrictive firewall config, that allows only basic networking & SSH.

This is only in effect until Docker is loaded in.

The actual Docker image will load in a much more intricate firewall.

```sh
# To make sure everything is in effect
reboot
```

## Step 2.

Run `docker-compose up --detach` on the [`docker-compose.yml`](https://github.com/ms-jpq/docker-home-router/tree/whale/install/docker-compose.yml).

You see most configs are in `docker-compose.yml` example.

---

## Pihole / Adguard Home

Pihole / Adguard must run on same machine as the router.

```yaml
pihole:
  # Everything as usual
  ...
  # Bind DNS ports to LOOPBACK, ie 127.69.69.69
  ports:
    - 127.69.69.69:53:53/tcp
    - 127.69.69.69:53:53/udp

router:
  environment:
    # Set DNS to same LOOPBACK
    - DNS_SERVERS=127.69.69.69#53
```

## Reverse Proxy

You do not need to do this if you do not want to do both:

1. Run reverse proxy on same machine as the router

2. Have the reverse proxy access `*.<hostname>.lan` DNS records

Note: [`guacd`](https://hub.docker.com/r/guacamole/guacd) is also a "reverse proxy".

```yaml
nginx/traefik/whatever:
  # Everything as usual
  ...
  # You have to use the following 3 lines
  network_mode: host
  dns:
    - 0:0:0:0:0:0:0:1
    - 127.0.0.1
```
