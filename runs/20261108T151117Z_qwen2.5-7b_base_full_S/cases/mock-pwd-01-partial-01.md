# mock-pwd-01-partial-01

- Control: **MOCK-PWD-01 — Password strength for workforce accounts**
- Expected status: **Partiellement conforme** (`partial`)
- Dataset rationale (human review only): Some safeguards are present, but at least one required scope, threshold, or follow-up condition is missing.
- Language: fr
- Tags: contradiction

## Control criteria

- The enforced minimum password length is at least 14 characters.
- A mix of character types or an equivalent breached-password check is enforced.
- The effective configuration agrees with the written policy.

## Repetition 1

- Verdict: **Non conforme** (`non_compliant`)
- Expected match: **no**
- Confidence: 0.9
- Retry count: 0; likely truncation: False
- Latency: 116.239 s; prompt/output tokens: 1232/347

- Backend prompt tokens: 1232; independent estimate: 1290

- Prompt processing speed: 25.0 tokens/s; generation speed: 5.2 tokens/s

### Justification

The minimum password length is set to 8 characters, which is less than the required 14 characters. Additionally, breached password blocking is not enabled, which is a requirement for password strength enforcement.

### Criterion assessment

- **no** — The enforced minimum password length is at least 14 characters.: The effective policy minimum length is 8 characters, which is below the required 14 characters.
- **unclear** — A mix of character types or an equivalent breached-password check is enforced.: The policy mentions complexity required but does not specify a mix of character types or a breached password check. Breached password blocking is disabled.
- **no** — The effective configuration agrees with the written policy.: The minimum length is set to 8 characters, which is less than the required 14 characters, and breached password blocking is not enabled.

### Quotes

- ✅ `effective-policy.ini`: minimum_length = 8
- ✅ `effective-policy.ini`: breached_password_block = false

### Recommendation

Increase the minimum password length to at least 14 characters and enable breached password blocking. Ensure that the effective configuration aligns with the written policy.
