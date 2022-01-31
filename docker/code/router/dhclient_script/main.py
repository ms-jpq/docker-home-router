



def main() -> None:
    if settings().interfaces.wan_pd_only and ipv6_enabled():
        try:
            lease = DHCP_CLIENT_LEASES.read_text()
        except FileNotFoundError:
            pass
        else:
            if network := _parse(lease):
                addrs = addr_show()
                if_up(
                    addrs,
                    interface=settings().interfaces.wan,
                    networks={network},
                )
