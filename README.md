# Docker Home Router

Yes, its a router that runs off of a single Docker image.

Yes, its packed with tons of features.

Yes, you can run it along side with other Docker images.

---

## Features

### Cool & for everybody

<details>
  <summary>
    <b>Fairness & prioritization</b>
  </summary>

Bandwidth is balanced on a (per-computer -> per-stream) basis.

Should help to alleviate any single computer from hogging the internet juice.

</details>

<details>
  <summary>
    <b>Better ping!</b>
  </summary>

As traffic approach maximum bandwidth, latency shoots up.

Thats why we do traffic shaping. :)

</details>

<details>
  <summary>
    <b>One way guest network</b>
  </summary>

You can talk to guests, guests can reply. Guest cannot initiate talks with you.

Pretty good to put all the untrusted stuff on the guest network.

</details>

<details>
  <summary>
    <b>VPN (1 step set-up)</b>
  </summary>

Just go to `http://<router-name>.lan:8888/` from (not your guest network) and BAM!

There are the QR codes you can scan on your phone, to add VPN profiles. (Need the official wireguard app).

You can add as many VPN profiles as you want!

</details>

<details>
  <summary>
    <b>Port forwarding based on hostname</b>
  </summary>

Yub, who cares about MAC addresses? Not us humans.

</details>

### Cool & for nerds

<details>
  <summary>
    <b>Run it along side other Docker images</b>
  </summary>

You can run this along other Docker images!

Need I say more?

</details>

<details>
  <summary>
    <b>DNS sinkhole</b>
  </summary>

All the outbound DNS traffic is redirected to a single server, your server.

Very cash money for running DNS based adblock, such as pihole, or adguardhome.

DOT is also blocked.

</details>

<details>
  <summary>
    <b>Wildcard LAN domains (`*.<hostname>.lan`)</b>
  </summary>

Suppose you have a computer called `<name>`. Most routers will let you use `<name>.lan` to visit `<name>`.

I go one step further. Everything under `*.<name>.lan` also goes to `<name>`.

Very useful for reverse proxies.

</details>

<details>
  <summary>
    <b>Simple split tunneling</b>
  </summary>

All you need to do is write down the IP ranges on the other side of your tunnel, the image will calculate to use non-overlapping local networks.

</details>

### Cool, but not that useful

<details>
  <summary>
    <b>Recursive DNS resolver (by default)</b>
  </summary>

If you are worried about your ISP fiddling with your DNS or something.

</details>

<details>
  <summary>
    <b>Network wide HTTP cache</b>
  </summary>

Not very useful these days, tbh, but kinda cool.

</details>

<details>
  <summary>
    <b>Visit TOR dark-web with regular browsers</b>
  </summary>

Visit `.onion` websites without having to setup TOR.

Disclaimer: This is purely for convenience / fun, not privacy.

Only works on non-🍎 devices because 🍎 locked this feature behind a VPN profile.

</details>

<details>
  <summary>
    <b>NTP sinkhole</b>
  </summary>

Force all your local devices to be in sync with your router's clock (and each other).

</details>

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
