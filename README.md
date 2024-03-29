# Docker Home Router

Yes, its a router that runs off of a single Docker image & 3 lines of script.

Yes, its packed with tons of features.

Yes, you can run it along side with other Docker images.

Yes, you only need to adjust [2 environmental variables to run](https://github.com/ms-jpq/docker-home-router/blob/whale/install/docker-compose.yml)

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

Just go to <code>http://router-name.lan:8888/wg/</code> from (not your guest network) and BAM!

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

Very cash money for running DNS based adblock, such as [pihole](https://pi-hole.net/), or [adguardhome](https://github.com/AdguardTeam/AdGuardHome).

DOT is also blocked.

</details>

<details>
  <summary>
    <b>Wildcard LAN domains (*.&lthostname&gt.lan)</b>
  </summary>

Suppose you have a computer called <code>name</code>. Most routers will let you use <code>name.lan</code> to visit <code>name</code>.

I go one step further. Everything under <code>\*.name.lan</code> also goes to <code>name</code>.

Very useful for reverse proxies.

</details>

<details>
  <summary>
    <b>Simple split tunneling</b>
  </summary>

All you need to do is write down the IP ranges on the other side of your tunnel, the image will automatically assign non-overlapping local networks.

</details>

<details>
  <summary>
    <b>Indepth Dashboard</b>
  </summary>

Go to <code>http://router-name.lan:8888/</code> (from not guest network), and you will see information on DHCP leases, forwarded ports, subnet assignment, firewall rules, HTTP cache performance, and packet scheduler statistics.

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

Visit <code>.onion</code> websites without having to setup TOR.

Disclaimer: This is purely for convenience / fun, not privacy.

Only works on non-🍎 devices because 🍎 [locked this feature behind a VPN profile](https://developer.apple.com/documentation/devicemanagement/vpn/dns).

</details>

<details>
  <summary>
    <b>NTP sinkhole</b>
  </summary>

Force all your local devices to be in sync with your router's clock (and each other).

</details>

---

## INSTALL.md

See [INSTALL.md](https://github.com/ms-jpq/docker-home-router/tree/whale/install)

---

## FAQ

<details>
  <summary>What is the easiest way to get extra ports for WAN/LAN/Guest?</summary>

USB 3 ethernet adapters are very cheap and are more than enough for sub gigabit speeds.

Gigabit PCIE adapters are also very cheap, but you need extra PCIE ports.

You can also get a VLAN capable switch, but those are slightly more $$$.

</details>

---

## Netplan


```yaml
---
version: 2
network:
  ethernets:
    "<wan if>":
      dhcp4: True
      dhcp6: True
      accept-ra: True
      ipv6-privacy: True
    # LAN ifs should be commented out
```


---

## WTF, Why???

### Docker

Because foremost, it's an amazing _immutable_ distribution format.

Clean install, clean uninstall, well known sandbox & runtime, popular configuration format, the upsides far out weigh the downsides for me.

Also works well with other Docker images, so I can justify spending $$$ on beefier hardware.

### NAT66

Same reason as NAT44, because you only need 1 <code>::/128</code> address.

Even tho in theory we have almost unlimited IP6 addresses, there are many situations, such as shared living arrangements, bad ISPs, normie landlords, etc, where you do not get a nice stable block of prefixes.

Kinda sucks, but it be like that sometimes.
