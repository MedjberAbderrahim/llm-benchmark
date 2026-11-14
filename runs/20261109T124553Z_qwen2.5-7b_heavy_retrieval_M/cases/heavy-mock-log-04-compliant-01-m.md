# heavy-mock-log-04-compliant-01-m

- Control: **MOCK-LOG-04 — Security event retention and availability**
- Expected status: **Conforme** (`compliant`)
- Dataset rationale (human review only): The cited policy and effective export satisfy the stated mock criteria.
- Language: mixed
- Tags: heavy, tier_M

## Control criteria

- Security records are retained for at least 365 days.
- At least the most recent 90 days are immediately searchable or otherwise readily available.
- The effective logging configuration supports the stated periods.

## Repetition 1

- Verdict: **Conforme** (`compliant`)
- Expected match: **yes**
- Confidence: 0.95
- Retry count: 0; likely truncation: False
- Latency: 186.356 s; prompt/output tokens: 2696/392

- Backend prompt tokens: 2696; independent estimate: 2744

- Prompt processing speed: 22.9 tokens/s; generation speed: 5.7 tokens/s

### Justification

The evidence shows that the security records are retained for 400 days, which is more than the required 365 days. Additionally, the most recent 100 days are immediately searchable, meeting the requirement of being readily available for at least 90 days. The effective logging configuration supports the stated periods, as evidenced by the settings in the event platform settings file.

### Criterion assessment

- **yes** — Security records are retained for at least 365 days.: The retention_days setting is 400 days, which exceeds the required 365 days.
- **yes** — At least the most recent 90 days are immediately searchable or otherwise readily available.: The searchable_days setting is 100 days, which is more than the required 90 days.
- **yes** — The effective logging configuration supports the stated periods.: The event platform settings and operational procedures indicate that the logging configuration supports the stated retention and searchable periods.

### Quotes

- ✅ `event-platform-settings.yaml`: retention_days: 400
searchable_days: 100
- ✅ `security-event-handling-standard.md`: Security events are archived for 400 days. The most recent 100 days remain indexed for immediate search.

### Recommendation

Maintain current logging and retention practices as they meet the stated criteria.

### Retrieval

- Chunks requested / returned to context: 5 / 5; shortfall: none; tokens sent: 1465
- Retrieval / query embedding: 0.005 s / 0.335 s
- Required gold passages in context: 2/2; all required: True
- Attribution: ok
