# heavy-mock-pwd-01-partial-01-m

- Control: **MOCK-PWD-01 — Password strength for workforce accounts**
- Expected status: **Partiellement conforme** (`partial`)
- Dataset rationale (human review only): Some safeguards are present, but at least one required scope, threshold, or follow-up condition is missing.
- Language: fr
- Tags: contradiction, heavy, tier_M

## Control criteria

- The enforced minimum password length is at least 14 characters.
- A mix of character types or an equivalent breached-password check is enforced.
- The effective configuration agrees with the written policy.

## Repetition 1

- Verdict: **Non conforme** (`non_compliant`)
- Expected match: **no**
- Confidence: 0.9
- Retry count: 0; likely truncation: False
- Latency: 222.161 s; prompt/output tokens: 3684/394

- Backend prompt tokens: 3684; independent estimate: 3221

- Prompt processing speed: 23.5 tokens/s; generation speed: 6.0 tokens/s

### Justification

Les preuves fournies indiquent que la longueur minimale de mot de passe est de 8 caractères, ce qui ne satisfait pas le critère d'un minimum de 14 caractères. De plus, il n'y a aucune mention d'un contrôle de complexité équivalent ou d'un blocage de mots de passe compromis.

### Criterion assessment

- **no** — The enforced minimum password length is at least 14 characters.: The effective policy shows a minimum length of 8 characters, which is below the required 14 characters.
- **unclear** — A mix of character types or an equivalent breached-password check is enforced.: There is no evidence of a complexity check or breached password block in the provided policy.
- **no** — The effective configuration agrees with the written policy.: The effective policy shows a minimum length of 8 characters, which does not align with the written policy requiring 12 characters.

### Quotes

- ✅ `identity-access-standard-v4.md`: La norme interne demande 12 caractères. Les administrateurs appliquent un contrôle de complexité.
- ✅ `identity-policy-export.ini`: [effective_policy] minimum_length = 8

### Recommendation

Reviser the password policy to enforce a minimum length of at least 14 characters and implement a complexity check or breached password block.

### Retrieval

- Chunks requested / returned to context: 5 / 5; shortfall: none; tokens sent: 1905
- Retrieval / query embedding: 0.004 s / 0.300 s
- Required gold passages in context: 2/2; all required: True
- Attribution: llm_error
