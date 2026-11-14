# heavy-mock-patch-05-compliant-01-m

- Control: **MOCK-PATCH-05 — Timely critical security updates**
- Expected status: **Conforme** (`compliant`)
- Dataset rationale (human review only): The cited policy and effective export satisfy the stated mock criteria.
- Language: en
- Tags: heavy, tier_M

## Control criteria

- Critical security updates are deployed within 30 calendar days of release or identification.
- The deadline applies to in-scope production systems.
- Records show due dates and completion or tracked exceptions.

## Repetition 1

- Verdict: **Partiellement conforme** (`partial`)
- Expected match: **no**
- Confidence: 0.7
- Retry count: 0; likely truncation: False
- Latency: 591.015 s; prompt/output tokens: 3389/473

- Backend prompt tokens: 3389; independent estimate: 3292

- Prompt processing speed: 8.1 tokens/s; generation speed: 2.7 tokens/s

### Justification

Le contrôle évalue la conformité des mises à jour de sécurité critiques déployées dans un délai de 30 jours. Les preuves montrent que le délai est de 20 jours, ce qui est plus strict que le contrôle, mais il n'est pas clair si tous les systèmes en production sont couverts. De plus, les preuves ne montrent pas clairement que les dates d'échéance et les dates de déploiement sont enregistrées pour tous les systèmes.

### Criterion assessment

- **unclear** — Critical security updates are deployed within 30 calendar days of release or identification.: Le délai est de 20 jours, ce qui est plus strict que le contrôle, mais il n'est pas clair si tous les systèmes en production sont couverts.
- **unclear** — The deadline applies to in-scope production systems.: Il n'est pas clair si tous les systèmes en production sont couverts par ce délai de 20 jours.
- **no** — Records show due dates and completion or tracked exceptions.: Les preuves ne montrent pas clairement que les dates d'échéance et les dates de déploiement sont enregistrées pour tous les systèmes.

### Quotes

- ✅ `asset-update-register.json`: "critical_deadline_days": 20
- ✅ `change-management-standard-v4.md`: Critical fixes for production assets are due within 20 calendar days.

### Recommendation

Il est recommandé de vérifier si tous les systèmes en production sont couverts par le délai de 20 jours et de s'assurer que les dates d'échéance et les dates de déploiement sont enregistrées pour tous les systèmes.

### Retrieval

- Chunks requested / returned to context: 5 / 5; shortfall: none; tokens sent: 1943
- Retrieval / query embedding: 0.011 s / 3.683 s
- Required gold passages in context: 2/2; all required: True
- Attribution: llm_error
