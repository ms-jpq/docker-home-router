# Docker Home Router

Yes, its a router that runs off of a single Docker image.

Yes, its packed with tons of features.

Yes, you can run it along side with other Docker images.

---

## Features

### Cool, for everybody

#### Fairness!

Bandwidth is balanced on a (per-computer -> per-stream) basis.

Should help to alleviate any single computer from hogging the internet juice.

#### One way guest network

You can talk to guests, guests can reply. Guest cannot initiate talks with you.

Pretty good to put all the untrusted stuff on the guest network.

#### VPN (1 step set-up)

Just go to `http://<router-name>.lan:8888/` from (not your guest network) and BAM!

There are the QR codes you can scan on your phone, to add VPN profiles. (Need the official wireguard app).

### Cool, for nerds

#### Run it along side other Docker images

You can run this along other Docker images!

Need I say more? :D :D :D

#### DNS sinkhole

All the outbound DNS traffic is redirected to a single server, your server.

Very cash money for running DNS based adblock, such as pihole, or adguardhome.

DOT is also blocked.

#### Wildcard LAN domains (`*.<hostname>.lan`)

Suppose you have a computer called `<name>`. Most routers will let use `<name>.lan` to visit `<name>`.

I go one step further. Everything under `*.<name>.lan` also goes to `<name>`.

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

#### NTP sinkhole

Force all your local devices to be in sync with your router's clock (and each other).

---

## WTF, Why???

### Docker

Because foremost, it's an amazing _immutable_ distribution format.

Clean install, clean uninstall, well known sandbox & runtime, popular configuration format, the upsides far out weigh the downsides for me.

Also works well with other Docker images, so I can justify spending $$$ on beefier hardware.

### NAT66

Same reason as NAT44, because you only need 1 `::/128` address, even tho in theory we have almost unlimited addresses.

There are many situations, such as shared living arrangements, bad ISPs, normie landlords, etc, where you do not get a nice stable block of addresses.

Kinda sucks, but it be like that sometimes.
