# heavy-mock-lock-03-non-compliant-01-m

- Control: **MOCK-LOCK-03 — Repeated sign-in failure handling**
- Expected status: **Non conforme** (`non_compliant`)
- Dataset rationale (human review only): The effective evidence shows a material failure against one or more required criteria.
- Language: en
- Tags: heavy, tier_M

## Control criteria

- Accounts are blocked or delayed after no more than 5 consecutive failures.
- The protective state lasts at least 15 minutes or requires an approved reset.
- The configured behavior is evidenced.

## Repetition 1

- Verdict: **Non conforme** (`non_compliant`)
- Expected match: **yes**
- Confidence: 1.0
- Retry count: 0; likely truncation: True
- Latency: 732.612 s; prompt/output tokens: 10383/402

- Backend prompt tokens: 10383; independent estimate: 9588

- Prompt processing speed: 16.8 tokens/s; generation speed: 3.6 tokens/s

### Justification

The evidence provided does not meet the criteria for the control. Specifically, the `authentication-export.json` file indicates that the `failed_attempt_threshold` is set to 0 and `lockout_enabled` is set to false. This means that no account lockout or delay is triggered after failed sign-ins, which directly contradicts the control's requirement that accounts should be blocked or delayed after no more than 5 consecutive failures. Additionally, the `authentication-operations-standard.md` file does not provide any evidence of a protective state lasting at least 15 minutes or requiring an approved reset.

### Criterion assessment

- **no** — Accounts are blocked or delayed after no more than 5 consecutive failures.: The `authentication-export.json` file shows `failed_attempt_threshold` is 0 and `lockout_enabled` is false.
- **no** — The protective state lasts at least 15 minutes or requires an approved reset.: There is no evidence of a protective state lasting at least 15 minutes or requiring an approved reset.
- **no** — The configured behavior is evidenced.: The `authentication-export.json` file does not provide evidence of the required protective behavior.

### Quotes

- ✅ `authentication-export.json`: "failed_attempt_threshold": 0, "lockout_enabled": false

### Recommendation

Implement a mechanism to block or delay accounts after no more than 5 consecutive failed sign-ins, and ensure that the protective state lasts at least 15 minutes or requires an approved reset.
