# Docker Home Router

You can talk to guest devices, not vice versa.

---

## What does it do?

### For Everybody

#### Per host / stream Fairness

- Good for torrenting

#### Lowered ping under load

#### Zero Conf :: Forget abot IP / MAC

Port forwarding is wack, you need to copy MAC & IP addresses around, hard to remember.

Why not just use `hostname`s ?

#### Guest zones with one way traffic filter

You can talk to guest devices, not vice versa.

Good for IOT.

### For VPN Users

#### Built-in Wireguard VPN

#### Conflict free IP addresses

Automagically calculates non-overlapping IPv4 addresses

#### DNS records for VPN clients

### For Developers

#### Wildcard subdomains for connected machines

`abc.<hostname>.lan` or `edf.<hostname>.lan` works the same as `<hostname>.lan`

---

## Limitations

You will have to run the same release of ubuntu as the image,

because I

---

## Why?

I am tired of
