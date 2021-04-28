# Docker Home Router

You can talk to guest devices, not vice versa.

---

## What does it do?

### For Everybody

#### Per host / stream Fairness

Are you mad that your roommate is hogging the internet?

What if we just **distribute bandwidth** on a per-computer basis?

Much better!

#### Lowered ping under load

Latency goes up dramatically when traffic exceeds bandwidth, making everything laggy.

What if we just shape traffic to **avoid congestion**?

**Good for torrenting**

#### Zero Conf :: Forget abot IP / MAC

Port forwarding is wack, you need to shuffle MAC & IP addresses around, hard for humans.

Especially for many machines.

Why not just **use the names of your computers**?

\*See the section on forwarding ports

#### Guest zones with one way traffic

The Internet of Things is convenient! The Internet of Things is insecure!

Why not just **put untrusted devices in a jail**?

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
