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

## Step 2.

Run `docker-compose up --detach` on the [`docker-compose.yml`](https://github.com/ms-jpq/docker-home-router/tree/whale/install/docker-compose.yml).

You see most configs are in `docker-compose.yml` example.

## Step 3.

Test everything works after rebooting, you are gucci.

```sh
reboot
```
