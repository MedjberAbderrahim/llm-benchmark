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
- Confidence: 0.8
- Retry count: 0; likely truncation: False
- Latency: 260.711 s; prompt/output tokens: 3391/459

- Backend prompt tokens: 3391; independent estimate: 3292

- Prompt processing speed: 20.3 tokens/s; generation speed: 4.9 tokens/s

### Justification

Le control de 'Timely critical security updates' est partiellement respecté. Bien que la procédure indique que les mises à jour critiques doivent être déployées dans un délai de 20 jours, il n'y a pas de preuves suffisantes que ce délai est respecté pour tous les systèmes en production. Les registres de mise à jour et les tickets de changement ne contiennent pas de preuves de déploiement dans les 20 jours pour tous les systèmes en production.

### Criterion assessment

- **no** — Critical security updates are deployed within 30 calendar days of release or identification.: Il n'y a pas de preuves que toutes les mises à jour critiques ont été déployées dans les 20 jours après leur identification.
- **yes** — The deadline applies to in-scope production systems.: La procédure indique que les mises à jour critiques pour les systèmes en production doivent être déployées dans un délai de 20 jours.
- **yes** — Records show due dates and completion or tracked exceptions.: Les registres de mise à jour et les tickets de changement contiennent des dates de déploiement et des exceptions suivies.

### Quotes

- ✅ `change-management-standard-v4.md`: Critical fixes for production assets are due within 20 calendar days. The ticket queue records discovery, due date, and deployment evidence.
- ❌ INVALID `asset-update-register.json`: critical_deadline_days: 20

### Recommendation

Recommander une amélioration de la traceabilité des déploiements de mises à jour critiques pour tous les systèmes en production.

### Retrieval

- Chunks requested / returned to context: 5 / 5; shortfall: none; tokens sent: 1943
- Retrieval / query embedding: 0.005 s / 3.423 s
- Required gold passages in context: 2/2; all required: True
- Attribution: llm_error
