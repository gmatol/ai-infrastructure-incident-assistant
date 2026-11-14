# Evaluation worksheet

Use one record per attempted run. Keep a separate row for each repeat and retain failures. A dash means not applicable or not measured. A failed request has an outcome and error category but no answer score.

| Run metadata | Entry |
| --- | --- |
| Case ID / version / repeat / prompt hash | |
| Date / application SHA / prompt variant or hash | |
| Entry point / runbook source and revision / model settings | |
| Configured model / returned model ID if available | |
| Mode (simulated, application model, or manual surrogate) / outcome / report or error reference | |

| Evidence to record | Entry |
| --- | --- |
| Instruction delivery | Captured system rule present/absent, expected message order, exact incident input match, runbook source or plain payload, schema passed. Link the corresponding simulated test result. Mark unobserved delivery as unobserved. |
| Actual model behavior | Returned enum; quote showing which users were asked about; quote showing which applications were asked about; explicit provisional wording; score for severity; confirmed scope and urgency if applicable; safety flags. |
| Diagnostic accuracy | Reference agreement (meets/partial/contradicts/unclear), cited facts, unsupported claims, check that would distinguish hypotheses, and recovery validation proposed. Record live cause verification separately as false for these fictional inputs. |
| Human review | Reviewer/date, six named scores and total /12, quote or step reference per score, disagreements and resolution, risk explanation and specific improvement. Use the existing scorer for saved CLI reports if useful. |
