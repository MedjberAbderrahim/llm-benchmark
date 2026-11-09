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
- Latency: 43.497 s; prompt/output tokens: 1198/315

### Justification

The minimum password length is set to 8 characters, which is less than the required 14 characters. Additionally, breached password blocking is not enabled, which is a requirement for password strength enforcement.

### Criterion assessment

- **no** — The enforced minimum password length is at least 14 characters.: The effective policy minimum length is 8 characters, which is less than the required 14 characters.
- **unclear** — A mix of character types or an equivalent breached-password check is enforced.: The effective policy requires complexity but does not mention breached password blocking.
- **no** — The effective configuration agrees with the written policy.: The minimum length requirement is not met, and breached password blocking is not enabled.

### Quotes

- ✅ `effective-policy.ini`: minimum_length = 8
- ✅ `effective-policy.ini`: breached_password_block = false

### Recommendation

Implement a minimum password length of at least 14 characters and enable breached password blocking to meet the security control requirements.
