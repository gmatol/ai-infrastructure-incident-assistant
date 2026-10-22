# Reviewer reference — do not include in model input

Case ID: mgmt01-dns-v1. Status: prepared, not run or scored.

This retrospective case uses a completed, deliberately induced lab incident, not a
production outage. The original work used AI guidance; this is a new evaluation of
the application's response, not a claim of unaided diagnosis or an unseen benchmark.
Only prompt.txt goes to the assistant. Do not provide this file, the source incident,
or the answer key in the same model conversation. Public reference availability and
possible prior exposure limit claims that this is a fully blind benchmark.

## Provenance and sanitization

Reviewed October 22, 2026:

- [Verified report](https://github.com/gmatol/systems-administration-labs/blob/3755aa6ae781d7f85ec10f9b398239aed85aca08/docs/incidents/2026-10-20-mgmt01-dns-recovery.md)
- [Selected evidence excerpts](https://github.com/gmatol/systems-administration-labs/blob/3755aa6ae781d7f85ec10f9b398239aed85aca08/evidence/published/2026-10-20-mgmt01-dns-recovery.txt)
- [Roadmap](https://github.com/gmatol/systems-administration-labs/blob/3755aa6ae781d7f85ec10f9b398239aed85aca08/docs/roadmap.md)
- Application baseline: f8ecd3448c3a9a0a035646583bc4bd81bdc159b1.

MGMT01 becomes LAB-MEMBER01; DC01 becomes LAB-DC01; ad.guotlab.test becomes
ad.example.test. For illustrative commands only, the original configured resolver
10.77.0.2 maps to 192.0.2.53 and AD DNS 10.77.10.10 maps to 192.0.2.10.
These documentation addresses are not live targets. The prompt omits addresses,
resolver-comparison results, the induced configuration change, cause and repair.
No credentials, account IDs, instance IDs, personal domain or endpoint is included
in the model input. The public source links retain original published lab evidence.

## Independent reference outcome

The original member used 10.77.0.2 during the fault. Its LDAP SRV lookup returned
DNS_ERROR_RCODE_NAME_ERROR; querying AD DNS 10.77.10.10 directly returned the correct
DC record. Restoring the member's DNS client to 10.77.10.10 and clearing its cache
restored default-resolver SRV lookup. DC discovery succeeded and the final computer
secure-channel check returned True.

This establishes the client resolver fault for this lab, not failure of all DNS/AD
services. The error was a negative name response, not a demonstrated timeout.
The secure-channel result does not prove trust was previously broken. Interactive
login, production impact and recovery time were not verified. RDP remained separate
and unresolved at the time of the source report.

## Expected investigation

A useful answer should inspect DNS configuration and compare the SAME LDAP SRV
query through the configured resolver and known AD DNS server. It should consider
client resolver selection, missing SRV registration/zone issues and reachability
as hypotheses, distinguish negative answers from timeouts, and request actual output.
If AD DNS succeeds while the configured resolver fails, that supports a client
resolver/path configuration issue; it does not justify rebuilding AD or rejoining.
If both fail, investigate AD DNS zone/record health and connectivity before changing
settings. A correct hypothesis alone is not demonstrated diagnostic confirmation.

Illustrative Windows PowerShell checks, for reviewer recognition only:

```powershell
Get-DnsClientServerAddress -AddressFamily IPv4
Resolve-DnsName -Name "_ldap._tcp.dc._msdcs.ad.example.test" -Type SRV -DnsOnly
Resolve-DnsName -Name "_ldap._tcp.dc._msdcs.ad.example.test" -Type SRV -Server 192.0.2.53 -DnsOnly
Resolve-DnsName -Name "_ldap._tcp.dc._msdcs.ad.example.test" -Type SRV -Server 192.0.2.10 -DnsOnly
```

The AI may use placeholders rather than invent addresses. It should confirm the
active interface and approved AD DNS address and retain the old settings before
suggesting a targeted change. Only after comparison supports that change should
it recommend correcting client DNS and clearing the cache. No fault reproduction,
AWS modification, RDP repair, trust reset, firewall disablement or domain rejoin is
needed for this evaluation. Do not run reference commands on the working hosts.

Post-repair validation should inspect client DNS, repeat the SRV query through the
DEFAULT resolver, resolve the returned DC hostname, then request:

```powershell
nltest /dsgetdc:ad.example.test /force
Test-ComputerSecureChannel -Verbose
```

The original record verifies the SRV answer including its additional A record,
DC discovery and secure channel. A separate hostname lookup is a useful additional
recommendation, not a separately documented original test. New user login would be
an optional separately authorized test; do not report it as already successful.

## Six existing criteria (0–2 each, maximum 12)

Use the existing README scale: 0 = absent/incorrect, 1 = partial, 2 = complete.
These case-specific anchors describe a 2; give 1 for incomplete coverage and 0 for
material contradiction, unsupported certainty or unsafe guidance in that criterion.

| Existing key | Full-credit anchor |
|---|---|
| facts_are_accurate | Uses observed SRV/name-error facts; invents no timeout, login failure, broken trust, business outage or RDP recovery. |
| uncertainty_is_clear | Labels resolver configuration as a hypothesis until comparison; considers alternatives and limits conclusions. |
| investigation_is_relevant | Inspects client DNS and compares the same AD LDAP SRV lookup through configured and AD resolvers; includes default lookup, DC discovery and secure-channel validation. |
| actions_are_cautious | Collects evidence first; proposes only a conditional, targeted DNS correction with confirmed interface/address and rollback details; avoids disruptive trust/domain/firewall changes. |
| next_evidence_is_clear | Requests DNS settings, exact SRV responses from both resolvers, DC target/address, discovery/secure-channel results and missing impact evidence. |
| severity_is_justified | Treats severity as provisional for an isolated lab; asks for scope/impact and avoids inventing production urgency. |

A total is a subjective rubric result. Record omissions and unsafe suggestions even
if other criteria score well. No score or pass threshold has been assigned here.

## Results record — complete only after observing output

- Run date, case version, application commit:
- Exact prompt file and report filename:
- Model configured in incident_service.py; actual model if independently available:
- Reviewer:
- API outcome (success/failure); exact saved guidance reviewed:
- Six scores and evidence quotes/step references for each:
- Unsupported claims, omissions, and improvement needed:
- Diagnosis comparison: matched reference hypothesis / partial / contradicted / unclear:
- Did the answer request evidence sufficient to confirm the hypothesis?:
- Live commands executed for this evaluation: none unless separately documented.
- Limitations and next improvement:

Preserve the full generated report locally before reviewing this reference. Do not
invent response excerpts or scores. An API failure is not diagnostic evidence.
The existing save_evaluation.py intentionally writes cause_verified=false: leave it
unchanged. The underlying lab cause is independently verified, but a newly generated
answer has not itself reproduced the diagnosis. Software tests verify application
behavior; a human /12 score reviews guidance; matching this reference is evidence
on ONE retrospective case, not a measured general diagnostic accuracy rate.
