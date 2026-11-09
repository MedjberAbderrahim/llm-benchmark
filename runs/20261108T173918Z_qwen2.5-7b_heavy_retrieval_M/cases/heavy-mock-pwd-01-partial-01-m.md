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

- Verdict: **À vérifier / En attente de preuve** (`insufficient_evidence`)
- Expected match: **no**
- Confidence: 0.7
- Retry count: 0; likely truncation: False
- Latency: 151.787 s; prompt/output tokens: 2611/379

- Backend prompt tokens: 2611; independent estimate: 2494

- Prompt processing speed: 27.6 tokens/s; generation speed: 6.6 tokens/s

### Justification

Les excerpts fournis ne contiennent aucune information pertinente concernant la longueur minimale des mots de passe, le type de caractères requis ou la vérification des mots de passe usés. Les excerpts sont principalement centrés sur la gestion documentaire et d'autres aspects opérationnels.

### Criterion assessment

- **no** — The enforced minimum password length is at least 14 characters.: Aucune information sur la longueur minimale des mots de passe n'est fournie dans les excerpts.
- **no** — A mix of character types or an equivalent breached-password check is enforced.: Aucune mention de la complexité des mots de passe ou de la vérification des mots de passe usés n'est présente dans les excerpts.
- **unclear** — The effective configuration agrees with the written policy.: Il n'y a pas d'informations sur la configuration effective des mots de passe, donc il est impossible de déterminer si elle correspond à la politique écrite.

### Quotes

- ✅ `01-needle-01-procedure_fr.md`: La norme interne demande 12 caractères. Les administrateurs appliquent un contrôle de complexité.

### Recommendation

Rechercher des informations supplémentaires sur la configuration effective des mots de passe et la conformité avec la politique écrite.

### Retrieval

- Chunks: 4; tokens sent: 1323
- Retrieval / query embedding: 0.005 s / 0.000 s
- Gold passages in context: 1/2
- Attribution: retrieval_miss
