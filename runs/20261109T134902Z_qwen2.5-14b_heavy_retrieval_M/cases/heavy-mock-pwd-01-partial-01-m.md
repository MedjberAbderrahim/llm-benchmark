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

- Verdict: **Partiellement conforme** (`partial`)
- Expected match: **yes**
- Confidence: 0.8
- Retry count: 0; likely truncation: False
- Latency: 532.963 s; prompt/output tokens: 3683/426

- Backend prompt tokens: 3683; independent estimate: 3221

- Prompt processing speed: 10.4 tokens/s; generation speed: 2.4 tokens/s

### Justification

Le contrôle évalue la longueur minimale des mots de passe et la complexité requise. La politique interne demande 12 caractères, mais la configuration effective est de 8 caractères. La complexité est requise par la politique, mais il n'est pas clair si une vérification de mots de passe compromis est effectivement mise en œuvre.

### Criterion assessment

- **no** — The enforced minimum password length is at least 14 characters.: La politique interne demande 12 caractères, mais la configuration effective est de 8 caractères.
- **unclear** — A mix of character types or an equivalent breached-password check is enforced.: La politique interne demande une complexité requise, mais il n'est pas clair si une vérification de mots de passe compromis est effectivement mise en œuvre.
- **no** — The effective configuration agrees with the written policy.: La politique interne demande 12 caractères, mais la configuration effective est de 8 caractères.

### Quotes

- ✅ `identity-access-standard-v4.md`: La norme interne demande 12 caractères. Les administrateurs appliquent un contrôle de complexité.
- ✅ `identity-policy-export.ini`: minimum_length = 8
complexity_required = true
breached_password_block = false

### Recommendation

Il est recommandé de mettre à jour la configuration effective pour qu'elle corresponde à la politique interne et d'appliquer une vérification de mots de passe compromis.

### Retrieval

- Chunks requested / returned to context: 5 / 5; shortfall: none; tokens sent: 1905
- Retrieval / query embedding: 0.005 s / 3.676 s
- Required gold passages in context: 2/2; all required: True
- Attribution: ok
