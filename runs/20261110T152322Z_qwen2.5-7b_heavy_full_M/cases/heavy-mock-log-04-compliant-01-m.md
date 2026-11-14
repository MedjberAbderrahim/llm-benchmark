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
- Latency: 778.804 s; prompt/output tokens: 10030/460

- Backend prompt tokens: 10030; independent estimate: 9413

- Prompt processing speed: 15.5 tokens/s; generation speed: 3.5 tokens/s

### Justification

The evidence provided meets all the criteria specified in the control. The logging settings in the event-platform-settings.yaml file indicate a retention period of 400 days and a searchable period of 100 days, which satisfies the requirements. The documentation in the security-event-handling-standard.md and operations-handbook-4232.md files also support these settings and describe the operational interfaces and handover processes.

### Criterion assessment

- **yes** — Security records are retained for at least 365 days.: The event-platform-settings.yaml file specifies a retention_days of 400, which exceeds the required 365 days.
- **yes** — At least the most recent 90 days are immediately searchable or otherwise readily available.: The event-platform-settings.yaml file specifies a searchable_days of 100, which exceeds the required 90 days.
- **yes** — The effective logging configuration supports the stated periods.: The security-event-handling-standard.md and operations-handbook-4232.md files document the logging and retention procedures, supporting the stated periods.

### Quotes

- ✅ `event-platform-settings.yaml`: retention_days: 400
searchable_days: 100
- ✅ `security-event-handling-standard.md`: Security events are archived for 400 days. The most recent 100 days remain indexed for immediate search.
- ✅ `operations-handbook-4232.md`: The event pipeline separates collection health, parser status, routing destination, and the owner who investigates delivery gaps.

### Recommendation

Maintain the current logging configuration and ensure ongoing compliance with the stated periods.
