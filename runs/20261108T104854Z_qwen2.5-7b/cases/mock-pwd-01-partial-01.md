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
- Latency: 54.348 s; prompt/output tokens: 1198/383

### Justification

The minimum password length is set to 8 characters, which is less than the required 14 characters. Additionally, breached password blocking is not enabled, which is a significant security gap.

### Criterion assessment

- **no** — The enforced minimum password length is at least 14 characters.: The effective policy minimum length is 8 characters, as stated in the 'effective-policy.ini' file.
- **unclear** — A mix of character types or an equivalent breached-password check is enforced.: The 'effective-policy.ini' file does not specify the use of a mix of character types or a breached-password check. The procedure mentions a complexity check, but it is not clear if this is equivalent to a breached-password check.
- **no** — The effective configuration agrees with the written policy.: The minimum password length in the effective policy (8 characters) is less than the required 14 characters, and breached password blocking is not enabled.

### Quotes

- ✅ `effective-policy.ini`: minimum_length = 8
- ✅ `procedure_fr.md`: La norme interne demande 12 caractères. Les administrateurs appliquent un contrôle de complexité.

### Recommendation

Implement a minimum password length of at least 14 characters and enable breached password blocking. Ensure that the effective configuration aligns with the written policy.
