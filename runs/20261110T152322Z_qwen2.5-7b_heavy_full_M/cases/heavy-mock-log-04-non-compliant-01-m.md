# heavy-mock-log-04-non-compliant-01-m

- Control: **MOCK-LOG-04 — Security event retention and availability**
- Expected status: **Non conforme** (`non_compliant`)
- Dataset rationale (human review only): The effective evidence shows a material failure against one or more required criteria.
- Language: en
- Tags: numeric_trap, heavy, tier_M

## Control criteria

- Security records are retained for at least 365 days.
- At least the most recent 90 days are immediately searchable or otherwise readily available.
- The effective logging configuration supports the stated periods.

## Repetition 1

- Verdict: **Non conforme** (`non_compliant`)
- Expected match: **yes**
- Confidence: 0.9
- Retry count: 0; likely truncation: True
- Latency: 790.870 s; prompt/output tokens: 10467/407

- Backend prompt tokens: 10467; independent estimate: 9561

- Prompt processing speed: 15.6 tokens/s; generation speed: 3.4 tokens/s

### Justification

The evidence indicates that the security records are retained for only 90 days, which does not meet the requirement of at least 365 days. Additionally, the most recent 90 days are immediately searchable, but the policy does not specify that the previous 365 days must be immediately searchable. The effective logging configuration does not support the stated periods.

### Criterion assessment

- **no** — Security records are retained for at least 365 days.: The retention_days setting in the collector-settings.ini file is set to 90 days, which is less than the required 365 days.
- **yes** — At least the most recent 90 days are immediately searchable or otherwise readily available.: The searchable_days setting in the collector-settings.ini file is set to 30 days, which is less than the required 90 days, but the policy states that the most recent 90 days are immediately searchable.
- **no** — The effective logging configuration supports the stated periods.: The effective logging configuration in the collector-settings.ini file does not support the required retention and searchable periods.

### Quotes

- ✅ `collector-settings.ini`: retention_days = 90
- ✅ `collector-settings.ini`: searchable_days = 30

### Recommendation

Increase the retention_days setting to at least 365 days and ensure that the searchable_days setting supports the required 90 days of immediate searchability.
