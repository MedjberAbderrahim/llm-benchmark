# heavy-mock-patch-05-partial-01-m

- Control: **MOCK-PATCH-05 — Timely critical security updates**
- Expected status: **Partiellement conforme** (`partial`)
- Dataset rationale (human review only): Some safeguards are present, but at least one required scope, threshold, or follow-up condition is missing.
- Language: en
- Tags: heavy, tier_M

## Control criteria

- Critical security updates are deployed within 30 calendar days of release or identification.
- The deadline applies to in-scope production systems.
- Records show due dates and completion or tracked exceptions.

## Repetition 1

- Verdict: **Partiellement conforme** (`partial`)
- Expected match: **yes**
- Confidence: 0.8
- Retry count: 0; likely truncation: False
- Latency: 416.044 s; prompt/output tokens: 2689/423

- Backend prompt tokens: 2689; independent estimate: 2775

- Prompt processing speed: 10.0 tokens/s; generation speed: 2.9 tokens/s

### Justification

Le contrôle évalue la conformité des mises à jour de sécurité critiques déployées dans un délai de 30 jours. Les preuves montrent que le délai est de 45 jours, ce qui est en dehors du délai spécifié. Cependant, les preuves montrent que les exceptions sont suivies et documentées.

### Criterion assessment

- **no** — Critical security updates are deployed within 30 calendar days of release or identification.: Le délai spécifié est de 45 jours, ce qui est en dehors du délai de 30 jours requis.
- **unclear** — The deadline applies to in-scope production systems.: Les preuves ne précisent pas explicitement si le délai de 45 jours s'applique aux systèmes de production en portée.
- **yes** — Records show due dates and completion or tracked exceptions.: Le fichier 'deployment-service-export.yaml' indique que les exceptions sont suivies ('exceptions_tracked: true').

### Quotes

- ✅ `change-management-standard-v4.md`: Critical updates should be installed within 45 days when operations allow. Exceptions are discussed at the monthly meeting.
- ✅ `deployment-service-export.yaml`: critical_deadline_days: 45
exceptions_tracked: true

### Recommendation

Il est recommandé de réviser la politique pour aligner le délai de déploiement des mises à jour critiques sur le délai de 30 jours spécifié dans le contrôle.

### Retrieval

- Chunks requested / returned to context: 5 / 5; shortfall: none; tokens sent: 1477
- Retrieval / query embedding: 0.007 s / 3.175 s
- Required gold passages in context: 2/2; all required: True
- Attribution: ok
