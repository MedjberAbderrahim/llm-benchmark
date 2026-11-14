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
- Latency: 684.092 s; prompt/output tokens: 10468/472

- Backend prompt tokens: 10468; independent estimate: 9561

- Prompt processing speed: 18.8 tokens/s; generation speed: 3.7 tokens/s

### Justification

The evidence indicates that the security records are retained for 90 days, but the most recent 30 days are not immediately searchable or otherwise readily available. The `collector-settings.ini` file specifies a `searchable_days` value of 30, but the actual implementation does not provide immediate searchability for the most recent 30 days, as evidenced by the lack of searchable event index or archive settings.

### Criterion assessment

- **no** — Security records are retained for at least 365 days.: The retention period is set to 90 days, which is less than the required 365 days.
- **no** — At least the most recent 90 days are immediately searchable or otherwise readily available.: The `searchable_days` value is set to 30, which is less than the required 90 days. The evidence does not indicate that the most recent 30 days are immediately searchable or otherwise readily available.
- **no** — The effective logging configuration supports the stated periods.: The `searchable_days` value is set to 30, which is less than the required 90 days. The evidence does not indicate that the most recent 30 days are immediately searchable or otherwise readily available.

### Quotes

- ✅ `collector-settings.ini`: searchable_days = 30
- ✅ `security-event-handling-standard.md`: Les journaux de sécurité sont conservés pendant 90 jours au total. Les 30 jours les plus récents sont consultables rapidement.

### Recommendation

Increase the retention period to at least 365 days and ensure that the most recent 90 days are immediately searchable or otherwise readily available. Review and update the logging configuration to support these requirements.
