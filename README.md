# Docker Home Router

Yes, its a router that runs off of a single Docker image.

Yes, its packed with tons of features.

---

## Features

### Cool, for everybody

#### Fairness!

Bandwidth is balanced on a (per-computer -> per-stream) basis.

Should help to alleviate any single computer from hogging the internet juice.

#### One way guest network

You can talk to guests, guests can reply. Guest cannot initiate talks with you.

Pretty good to put all the untrusted stuff on the guest network.

### Cool, for nerds

#### DNS sinkhole

All the outbound DNS traffic is redirected to a single server, your server.

Very cash money for running DNS based adblock, such as pihole, or adguardhome.

DOT is also blocked.

#### Wildcard LAN domains (`*.<hostname>.lan`)

Suppose you have a computer called `ape`. Most routers will let use `ape.lan` to visit `ape`.

I go one step further. Everything under `*.ape.lan` also goes to `ape`.

Very useful for reverse proxies.

### Cool, but not that useful

#### Recursive DNS resolver (by default)

If you are worried about your ISP fiddling with your DNS or something.

#### Network wide HTTP cache

Not very useful these days, tbh, but kinda cool.

#### Visit TOR dark-web with regular browsers

Visit `.onion` websites without having to setup TOR.

Disclaimer: This is purely for convenience / fun, not privacy.

_Only works on non-fapple devices because 🍎 is very paternalistic_


---

## Why???

### Docker

### NAT66
