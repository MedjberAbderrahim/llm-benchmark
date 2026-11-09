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
- Confidence: 1.0
- Retry count: 0; likely truncation: False
- Latency: 235.287 s; prompt/output tokens: 1198/483

### Justification

Le contrôle de la longueur minimale du mot de passe est inférieur à 14 caractères et le contrôle de complexité n'est pas équivalent à une vérification de mots de passe compromis. De plus, la politique écrite demande 12 caractères, ce qui est également en dessous du seuil requis.

### Criterion assessment

- **no** — The enforced minimum password length is at least 14 characters.: La politique effective indique une longueur minimale de 8 caractères, ce qui est en dessous du seuil requis de 14 caractères.
- **no** — A mix of character types or an equivalent breached-password check is enforced.: La politique effective ne bloque pas les mots de passe compromis et ne nécessite pas de mélange de types de caractères.
- **unclear** — The effective configuration agrees with the written policy.: La politique écrite demande 12 caractères, mais la politique effective indique une longueur minimale de 8 caractères. De plus, la politique écrite n'est pas encore déployée dans l'Active Directory.

### Quotes

- ✅ `effective-policy.ini`: [effective_policy]
minimum_length = 8
complexity_required = true
breached_password_block = false
- ✅ `procedure_fr.md`: La norme interne demande 12 caractères. Les administrateurs appliquent un contrôle de complexité.
- ✅ `procedure_fr.md`: The service rollout note says the 12-character requirement has not yet reached the active directory policy.

### Recommendation

Mettre à jour la politique effective pour inclure une longueur minimale de 14 caractères et un contrôle de mots de passe compromis.
