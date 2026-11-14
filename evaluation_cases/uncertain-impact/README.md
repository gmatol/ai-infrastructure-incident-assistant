# Uncertain incident impact evaluation

Version 1. Eight fictional incident inputs are ready for evaluation.

## Run inputs

Use only the selected single-line file in [prompts](prompts/). Keep the [reviewer reference](REFERENCE.md) outside the model context. Copy the [worksheet](WORKSHEET.md) for each attempt. Keep outputs and review notes local until reviewed.

## Implementation reviewed


On main at [156d964](https://github.com/gmatol/ai-infrastructure-incident-assistant/tree/156d9641c66cebf80cc38e52703bc5ed324b6085), the shared analyzer sends the impact rule as a system message to `responses.parse` for plain prompts and runbook-wrapped prompts. The schema permits Low, Medium, High and Critical. To express provisional severity, the model must qualify the enum in a text field. For this evaluation, the qualification must be easy to find and clearly refer to the displayed rating. The API and CLI use the shared analyzer.

[PR #30](https://github.com/gmatol/ai-infrastructure-incident-assistant/pull/30) reports 57 local tests and Ruff passing, simulated checks for both request paths, and two earlier impact scores that moved from 1/2 to 2/2. At the inspected tip, `test_incident_service.py` covers input trimming, blank input and parsed output handling. `test_api_runbook_context.py` checks the DNS match and plain Linux payload with a fixed fake response. Neither asserts the new system instruction in both captured calls. The CLI runbook tests cover the corresponding CLI integration. `save_evaluation.py` uses six 0–2 scores, saves one evaluation per report and records `cause_verified=false`. The existing [MGMT01 case](https://github.com/gmatol/ai-infrastructure-incident-assistant/tree/156d9641c66cebf80cc38e52703bc5ed324b6085/evaluation_cases/mgmt01-dns) provides the single-line prompt and separate reviewer reference pattern.

## Compare results


1. **Check instruction delivery offline.** Capture arguments with a simulated client on a plain Linux input and an AD DNS input with a runbook. Check the system message includes both required questions and provisional wording on current main, while the pre-PR baseline omits the rule. Check the payload and schema are equivalent between variants. Record this in the delivery column only. A fixed mock answer gives no behavior score.
2. **Run a matched model comparison when execution is authorized.** Use the PR merge's first parent (`174115fa7ddd39799cf55814ddf7bedf12bc1bd9`) and merge commit (`a6f1eb09ea16a6c1db1f102f2ac06ebc2a3c080c`) to isolate the three-line instruction change. Use current main for the candidate instead only after confirming relevant behavior and context match the merge commit, or report any extra differences. Hold model ID, settings, entry point, schema, case text and per-case runbook selection fixed. Start fresh for each attempt. Alternate variant order and mask prompt-version labels during scoring. One pass per condition gives 16 attempts. Three repeats per condition give 48 attempts before retries. Start with one pass and use repeats if authorized to probe run-to-run variation. An offline real model or manually pasted prompt can pilot the worksheet. Report its environment and schema differences as surrogate evidence.
3. **Report counts with denominators.** For each variant, show attempted, valid and failed runs. Among valid unknown-impact runs, count those meeting all three checks (users, applications, provisional wording). Among valid confirmed-impact runs, count those meeting scope and urgency anchors. For each case, compare severity scores and flag regressions, diagnostic reference agreement and unsafe outputs separately. Report repeat disagreement where observed. Review flagged outputs even if the total improves. Use “On these eight fictional cases with [model/configuration], [x/y] met the impact criterion.” Avoid model-wide reliability estimates from this sample or combining the two earlier experiments with new results.
4. **Review independently where possible.** Score against this reference after capturing output. Ask a second reviewer to independently score flagged or borderline runs if available. Keep both initial scores and record how disagreements were resolved. Otherwise record that a single reviewer scored the run.

| Prompt variant | Attempted / valid / failed | Unknown all three / valid unknown | Confirmed scope + urgency / valid confirmed | Severity 2/2 / valid | Safety flags by case | Diagnostic agreement by case |
| --- | --- | --- | --- | --- | --- | --- |
| Pre-PR #30 | | | | | | |
| PR #30 | | | | | | |
