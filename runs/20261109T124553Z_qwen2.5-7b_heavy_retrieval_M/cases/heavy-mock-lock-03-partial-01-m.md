# heavy-mock-lock-03-partial-01-m

- Control: **MOCK-LOCK-03 — Repeated sign-in failure handling**
- Expected status: **Partiellement conforme** (`partial`)
- Dataset rationale (human review only): Some safeguards are present, but at least one required scope, threshold, or follow-up condition is missing.
- Language: mixed
- Tags: heavy, tier_M

## Control criteria

- Accounts are blocked or delayed after no more than 5 consecutive failures.
- The protective state lasts at least 15 minutes or requires an approved reset.
- The configured behavior is evidenced.

## Repetition 1

- Verdict: **Partiellement conforme** (`partial`)
- Expected match: **yes**
- Confidence: 0.85
- Retry count: 0; likely truncation: False
- Latency: 195.324 s; prompt/output tokens: 2695/401

- Backend prompt tokens: 2695; independent estimate: 2796

- Prompt processing speed: 21.9 tokens/s; generation speed: 5.6 tokens/s

### Justification

Le contrôle de sécurité est partiellement satisfait car les limites de tentatives de connexion et la durée du blocage sont configurées, mais les détails spécifiques de la configuration ne sont pas clairement établis dans les documents fournis.

### Criterion assessment

- **no** — Accounts are blocked or delayed after no more than 5 consecutive failures.: Les documents indiquent que 8 tentatives de connexion consécutives sont nécessaires avant un blocage, ce qui ne correspond pas à la limite de 5 tentatives spécifiée dans le contrôle.
- **no** — The protective state lasts at least 15 minutes or requires an approved reset.: Les documents ne spécifient pas la durée exacte du blocage, mais indiquent qu'il est de 10 minutes, ce qui est inférieur à la durée minimale de 15 minutes requise.
- **yes** — The configured behavior is evidenced.: Les paramètres de blocage après des tentatives de connexion consécutives sont configurés et documentés dans 'identity-service-settings.yaml'.

### Quotes

- ✅ `identity-service-settings.yaml`: failed_attempt_threshold: 8
lockout_minutes: 10

### Recommendation

Reviser la configuration pour aligner avec les exigences du contrôle, en particulier pour réduire le seuil de tentatives de connexion consécutives et augmenter la durée du blocage.

### Retrieval

- Chunks requested / returned to context: 5 / 5; shortfall: none; tokens sent: 1526
- Retrieval / query embedding: 0.005 s / 0.315 s
- Required gold passages in context: 2/2; all required: True
- Attribution: ok
