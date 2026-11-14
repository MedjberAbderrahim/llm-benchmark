# heavy-mock-lock-03-partial-01-m

- Control: **MOCK-LOCK-03 — Repeated sign-in failure handling**
- Expected status: **Partiellement conforme** (`partial`)
- Dataset rationale (human review only): Some safeguards are present, but at least one required scope, threshold, or follow-up condition is missing.
- Language: mixed
- Tags: heavy, tier_M

## Control criteria

- Accounts are blocked or delayed after no more than 5 consecutive failures.
- The protective state lasts at least 15 minutes or requires an approved reset.
- The configured behavior is evidenced.

## Repetition 1

- Verdict: **Non conforme** (`non_compliant`)
- Expected match: **no**
- Confidence: 0.9
- Retry count: 0; likely truncation: True
- Latency: 683.663 s; prompt/output tokens: 10387/334

- Backend prompt tokens: 10387; independent estimate: 9545

- Prompt processing speed: 17.8 tokens/s; generation speed: 3.4 tokens/s

### Justification

The evidence provided does not meet the criteria for the control. Specifically, the failed_attempt_threshold is set to 8, which exceeds the maximum of 5 consecutive failures allowed by the control. Additionally, there is no evidence of a protective state lasting at least 15 minutes or requiring an approved reset.

### Criterion assessment

- **no** — Accounts are blocked or delayed after no more than 5 consecutive failures.: The failed_attempt_threshold is set to 8, which is higher than the allowed 5 consecutive failures.
- **no** — The protective state lasts at least 15 minutes or requires an approved reset.: There is no evidence of a protective state lasting at least 15 minutes or requiring an approved reset.
- **no** — The configured behavior is evidenced.: The evidence does not provide any documentation or configuration that supports the required behavior.

### Quotes

- ✅ `identity-service-settings.yaml`: failed_attempt_threshold: 8
lockout_minutes: 10

### Recommendation

Adjust the failed_attempt_threshold to 5 or less and ensure that a protective state lasting at least 15 minutes or requiring an approved reset is implemented.
