# Windows Active Directory DNS checks

Use when a Windows domain member cannot resolve Active Directory services.

1. Record the affected hostname and exact DNS error.
2. Inspect the DNS servers configured on the affected computer.
3. Check Active Directory LDAP SRV record resolution.
4. Compare results from the configured resolver and the intended AD DNS server.
5. If an incorrect DNS configuration is confirmed, follow the approved change process.
6. After correction, verify DNS resolution, domain-controller discovery, and the computer secure channel.

A separate RDP connection failure requires its own investigation.


Collect evidence before changing DNS settings.