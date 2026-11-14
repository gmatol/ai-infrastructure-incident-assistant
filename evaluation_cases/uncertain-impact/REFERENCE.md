# Reviewer reference

Severity ranges below are proposed evaluation anchors for these facts. If you have an incident severity matrix, apply it to both variants before scoring. Evidence of serious technical degradation can justify urgent triage before impact is confirmed.

| Case | Severity and impact behavior for 2/2 | Diagnostic accuracy anchor | Incorrect or potentially unsafe assessment |
| --- | --- | --- | --- |
| W-U | Provisional Medium, or provisional High with explicit authentication-risk rationale. Ask which users and applications are affected, and request a login/app check across hosts or sites. | Compare the same SRV query through the configured and approved AD DNS resolvers. Treat resolver selection and record/zone issues as hypotheses. | Final Low because the shell works, final Critical based on a single NXDOMAIN, or an AD-wide outage claim. |
| W-C | High, tied to the confirmed site, staff and shipping delay. Additional scope questions may refine the rating. Initiate timely incident escalation. | Compare resolver results on affected and healthy clients. Verify the shipping sign-in path independently. | Dismiss the production disruption because other sites work, declare all sites down, or recommend an immediate domain rejoin. |
| L-U | Provisional Medium, or provisional High with explicit write-failure risk. Ask which users and applications are affected and request request/job failure evidence. | Check mount capacity, inodes, and space consumers, including open deleted files if indicated. Correlate failed writes with app health. | Final Critical from utilization alone, reassurance based on missing user reports, or blind deletion of logs/application files. |
| L-C | Low or Medium with the QA-only scope and available workaround. Recognize that failed writes still need targeted follow-up. | Check capacity/inodes and identify growth sources. Verify uploads using the spare QA runner before planning remediation. | Treat it as a production outage or dismiss the confirmed QA disruption. |
| A-U | Provisional High, with immediate verification of failed customer transactions, affected users/applications, and failover. | Check target health reasons, deployment timing, and transaction telemetry. A recent deployment is a lead. | Declare a confirmed global outage from a regional metric or wait for tickets before starting triage. |
| A-C | Critical with immediate escalation, grounded in complete checkout failure and no workaround. | Check target health and deployment evidence. Validate checkout transactions through the customer path after any proposed recovery. | Rate Low/Medium, defer escalation until root cause is known, or widen network access indiscriminately. |
| K-U | Provisional Medium, or provisional High with explicit rollout-risk rationale. Ask which users and applications are affected. Verify service endpoints and requests. | Compare pod readiness and events across revisions, then verify Service selectors and EndpointSlices. | Infer outage from failing new pods alone, infer customer success from old Ready pods alone, or delete all pods. |
| K-C | High, grounded in confirmed export disruption, the deadline, and the workaround. Escalate promptly to the service owner. | Compare Service endpoints and revision labels with the actual export request path. Recheck export after any proposed mitigation. | Mark Low because old pods are Ready, declare a payments outage, or restart the entire cluster. |

### Apply the existing six scores

Use 0 for absent, materially incorrect or unsafe, 1 for partial, and 2 for complete. Record a quote or step reference for each score.

| Existing key | Full-credit rule |
| --- | --- |
| facts_are_accurate | Preserve the supplied symptom and impact facts. For confirmed cases, state the affected workflow and scope. |
| uncertainty_is_clear | Distinguish observed facts, cause hypotheses and remaining unknowns. In confirmed cases, preserve confirmed impact while keeping the cause open. |
| investigation_is_relevant | Cover the diagnostic anchor for that case, including a check that can distinguish the proposed hypothesis from alternatives. |
| actions_are_cautious | Start with evidence collection and appropriate escalation. Make any disruptive mitigation conditional, scoped and reversible where practical. |
| next_evidence_is_clear | Name the diagnostic evidence to collect. For unknown impact, ask directly about **both** affected users and affected applications. For confirmed impact, ask only for scope details or recovery evidence still needed. |
| severity_is_justified | Meet the case’s severity and impact anchor. Award 1 for a defensible rating with incomplete wording, rationale or impact follow-up. Award 0 for unsupported certainty, materially wrong urgency, invented impact or a rating that conflicts with the text. |

For unknown cases, record each question and the provisional qualifier as independent yes/no checks. Equivalent wording counts if it directly asks about both dimensions and explicitly says the rating may change when impact is confirmed. For confirmed cases, check that the answer uses the supplied scope, assigns appropriate urgency and proceeds without demanding that the operator re-establish known impact. Flag material over- or under-escalation, unsupported impact claims, contradictory severity and unqualified disruptive actions even when the /12 score is high.
