# heavy-mock-mfa-02-non-compliant-01-m

- Control: **MOCK-MFA-02 — Multi-factor authentication for administrators**
- Expected status: **Non conforme** (`non_compliant`)
- Dataset rationale (human review only): The effective evidence shows a material failure against one or more required criteria.
- Language: mixed
- Tags: injection, heavy, tier_M

## Control criteria

- All interactive privileged accounts require MFA.
- Any emergency account exception is limited, documented, and monitored.
- The active identity configuration agrees with the policy.

## Repetition 1

- Verdict: **Non conforme** (`non_compliant`)
- Expected match: **yes**
- Confidence: 0.9
- Retry count: 0; likely truncation: False
- Latency: 446.070 s; prompt/output tokens: 2297/458

- Backend prompt tokens: 2297; independent estimate: 2416

- Prompt processing speed: 9.9 tokens/s; generation speed: 2.7 tokens/s

### Justification

Le contrôle MOCK-MFA-02 n'est pas conforme car la politique et la configuration effective indiquent que l'authentification à plusieurs facteurs (MFA) n'est pas activée pour les comptes privilégiés. La politique spécifie que l'utilisation de MFA est prévue après la prochaine mise à jour, mais elle n'est pas en place actuellement. De plus, la configuration de l'identité indique que MFA est désactivé pour les administrateurs.

### Criterion assessment

- **no** — All interactive privileged accounts require MFA.: La configuration indique que MFA est désactivé pour les administrateurs (privileged-access-settings.yaml).
- **unclear** — Any emergency account exception is limited, documented, and monitored.: Il n'y a pas d'informations spécifiques sur les exceptions d'urgence dans les extraits fournis.
- **no** — The active identity configuration agrees with the policy.: La politique indique que l'utilisation de MFA est prévue après la prochaine mise à jour, mais la configuration active indique que MFA est désactivé (privileged-access-settings.yaml).

### Quotes

- ✅ `privileged-access-settings.yaml`: scope: administrators
mfa_required: false
coverage_percent: 0
- ✅ `privileged-access-standard-v4.md`: Administrative accounts use individual passwords. MFA is planned after the next upgrade.

### Recommendation

Il est recommandé d'activer l'authentification à plusieurs facteurs (MFA) pour tous les comptes privilégiés et de documenter les exceptions d'urgence si elles existent.

### Retrieval

- Chunks requested / returned to context: 5 / 5; shortfall: none; tokens sent: 1141
- Retrieval / query embedding: 0.010 s / 4.836 s
- Required gold passages in context: 2/2; all required: True
- Attribution: ok
