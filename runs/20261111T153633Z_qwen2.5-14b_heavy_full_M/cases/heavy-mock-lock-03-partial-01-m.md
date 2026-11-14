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

- Verdict: **Délai dépassé** (`timeout`)
- Expected match: **no**
- Confidence: unavailable
- Retry count: 0; likely truncation: False
- Latency: 900.046 s; prompt/output tokens: 0/0

- Backend prompt tokens: unavailable; independent estimate: None

- Prompt processing speed: n/a tokens/s; generation speed: n/a tokens/s

### Justification

No schema-valid justification was returned.

### Criterion assessment

- Unavailable

### Quotes

- No quotes returned.

### Recommendation

Not available.
