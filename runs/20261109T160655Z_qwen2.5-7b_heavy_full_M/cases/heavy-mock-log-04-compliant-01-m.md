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
- Confidence: 1.0
- Retry count: 0; likely truncation: False
- Latency: 665.443 s; prompt/output tokens: 10031/475

- Backend prompt tokens: 10031; independent estimate: 9413

- Prompt processing speed: 18.8 tokens/s; generation speed: 3.6 tokens/s

### Justification

The evidence provided shows that the logging and retention settings meet the criteria. The `event-platform-settings.yaml` file explicitly states a retention period of 400 days and a searchable period of 100 days, which aligns with the control requirements. The `security-event-handling-standard.md` and `operations-handbook-4232.md` documents also reinforce the stated periods and the effective logging configuration.

### Criterion assessment

- **yes** — Security records are retained for at least 365 days.: The `event-platform-settings.yaml` file specifies a retention_days of 400, which exceeds the required 365 days.
- **yes** — At least the most recent 90 days are immediately searchable or otherwise readily available.: The `event-platform-settings.yaml` file specifies a searchable_days of 100, which exceeds the required 90 days.
- **yes** — The effective logging configuration supports the stated periods.: The `event-platform-settings.yaml` file explicitly sets the retention_days and searchable_days to 400 and 100, respectively, which are in line with the stated periods.

### Quotes

- ✅ `event-platform-settings.yaml`: retention_days: 400
searchable_days: 100
- ✅ `security-event-handling-standard.md`: Security events are archived for 400 days. The most recent 100 days remain indexed for immediate search.
- ✅ `operations-handbook-4232.md`: The event pipeline separates collection health, parser status, routing destination, and the owner who investigates delivery gaps.

### Recommendation

Maintain the current logging and retention settings to ensure compliance with the security control.
