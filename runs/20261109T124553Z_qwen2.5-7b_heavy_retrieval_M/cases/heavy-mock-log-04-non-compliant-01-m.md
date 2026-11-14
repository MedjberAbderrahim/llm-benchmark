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

- Verdict: **Sortie invalide** (`invalid_output`)
- Expected match: **no**
- Confidence: unavailable
- Retry count: 1; likely truncation: True
- Latency: 521.039 s; prompt/output tokens: 7303/1024

- Backend prompt tokens: 7303; independent estimate: 3187

- Prompt processing speed: 21.9 tokens/s; generation speed: 5.5 tokens/s

### Justification

No schema-valid justification was returned.

### Criterion assessment

- Unavailable

### Quotes

- No quotes returned.

### Recommendation

Not available.

### Retrieval

- Chunks requested / returned to context: 5 / 5; shortfall: none; tokens sent: 1884
- Retrieval / query embedding: 0.004 s / 0.309 s
- Required gold passages in context: 2/2; all required: True
- Attribution: llm_error
