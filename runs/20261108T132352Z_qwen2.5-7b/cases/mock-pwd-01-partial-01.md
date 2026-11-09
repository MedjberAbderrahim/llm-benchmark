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
- Confidence: 0.95
- Retry count: 0; likely truncation: False
- Latency: 101.431 s; prompt/output tokens: 1198/328

### Justification

The minimum password length is set to 8 characters, which is less than the required 14 characters. Additionally, breached password blocking is not enabled, which is a requirement for password strength. The policy does not align with the written requirements.

### Criterion assessment

- **no** — The enforced minimum password length is at least 14 characters.: The effective policy sets the minimum length to 8 characters, which is below the required 14 characters.
- **no** — A mix of character types or an equivalent breached-password check is enforced.: Breached password blocking is disabled in the effective policy.
- **no** — The effective configuration agrees with the written policy.: The effective policy does not meet the minimum length requirement and lacks breached password blocking, contradicting the written policy.

### Quotes

- ✅ `effective-policy.ini`: minimum_length = 8
- ✅ `effective-policy.ini`: breached_password_block = false

### Recommendation

Update the effective policy to enforce a minimum password length of at least 14 characters and enable breached password blocking.
