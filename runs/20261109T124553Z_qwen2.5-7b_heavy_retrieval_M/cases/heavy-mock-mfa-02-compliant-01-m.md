# heavy-mock-mfa-02-compliant-01-m

- Control: **MOCK-MFA-02 — Multi-factor authentication for administrators**
- Expected status: **Conforme** (`compliant`)
- Dataset rationale (human review only): The cited policy and effective export satisfy the stated mock criteria.
- Language: fr
- Tags: heavy, tier_M

## Control criteria

- All interactive privileged accounts require MFA.
- Any emergency account exception is limited, documented, and monitored.
- The active identity configuration agrees with the policy.

## Repetition 1

- Verdict: **Non conforme** (`non_compliant`)
- Expected match: **no**
- Confidence: 0.8
- Retry count: 0; likely truncation: False
- Latency: 246.239 s; prompt/output tokens: 3787/359

- Backend prompt tokens: 3787; independent estimate: 3203

- Prompt processing speed: 22.2 tokens/s; generation speed: 4.8 tokens/s

### Justification

Les preuves fournies ne montrent pas que tous les comptes d'administrateurs interactifs nécessitent l'authentification multifactorielle (MFA). Les documents ne contiennent pas de preuves concrètes que l'authentification MFA est activée pour tous les comptes d'administrateurs interactifs. De plus, il n'y a aucune mention d'exceptions d'urgence limitées, documentées et surveillées.

### Criterion assessment

- **no** — All interactive privileged accounts require MFA.: Insufficient evidence to determine if all interactive privileged accounts require MFA.
- **no** — Any emergency account exception is limited, documented, and monitored.: No evidence of limited, documented, and monitored emergency account exceptions.
- **unclear** — The active identity configuration agrees with the policy.: Insufficient evidence to determine if the active identity configuration agrees with the policy.

### Quotes

- ✅ `privileged-access-standard-v4.md`: All interactive privileged users must complete a password and a hardware or app-based second factor. A monitored emergency identity is excluded and reviewed monthly.

### Recommendation

Implement MFA for all interactive privileged accounts and ensure that any emergency account exceptions are limited, documented, and monitored.

### Retrieval

- Chunks requested / returned to context: 5 / 5; shortfall: none; tokens sent: 1896
- Retrieval / query embedding: 0.004 s / 0.282 s
- Required gold passages in context: 1/2; all required: False
- Attribution: retrieval_miss
