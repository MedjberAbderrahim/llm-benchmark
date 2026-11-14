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
- Confidence: 0.8
- Retry count: 0; likely truncation: False
- Latency: 469.440 s; prompt/output tokens: 2693/490

- Backend prompt tokens: 2693; independent estimate: 2796

- Prompt processing speed: 9.3 tokens/s; generation speed: 2.7 tokens/s

### Justification

Le contrôle évalue la gestion des tentatives de connexion infructueuses, mais les paramètres spécifiques ne correspondent pas aux critères énoncés. Le compte est bloqué après 8 échecs consécutifs, ce qui dépasse le seuil de 5 échecs consécutifs. La durée du blocage est de 10 minutes, ce qui est inférieure à la durée minimale de 15 minutes requise. Il n'y a pas de preuve claire que le comportement configuré est documenté ou vérifié.

### Criterion assessment

- **no** — Accounts are blocked or delayed after no more than 5 consecutive failures.: Le compte est bloqué après 8 échecs consécutifs, ce qui dépasse le seuil de 5 échecs consécutifs.
- **no** — The protective state lasts at least 15 minutes or requires an approved reset.: La durée du blocage est de 10 minutes, ce qui est inférieure à la durée minimale de 15 minutes requise.
- **unclear** — The configured behavior is evidenced.: Il n'y a pas de preuve claire que le comportement configuré est documenté ou vérifié.

### Quotes

- ✅ `authentication-operations-standard.md`: Après 8 échecs consécutifs, le compte est temporairement bloqué. La durée du blocage dépend du service.
- ✅ `identity-service-settings.yaml`: failed_attempt_threshold: 8
lockout_minutes: 10

### Recommendation

Il est recommandé de réviser les paramètres de blocage pour qu'ils correspondent aux critères énoncés. De plus, il est nécessaire de documenter et de vérifier le comportement configuré.

### Retrieval

- Chunks requested / returned to context: 5 / 5; shortfall: none; tokens sent: 1526
- Retrieval / query embedding: 0.005 s / 3.187 s
- Required gold passages in context: 2/2; all required: True
- Attribution: ok
