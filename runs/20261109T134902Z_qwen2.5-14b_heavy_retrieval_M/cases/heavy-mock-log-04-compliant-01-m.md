# heavy-mock-log-04-compliant-01-m

- Control: **MOCK-LOG-04 — Security event retention and availability**
- Expected status: **Conforme** (`compliant`)
- Dataset rationale (human review only): The cited policy and effective export satisfy the stated mock criteria.
- Language: mixed
- Tags: heavy, tier_M

## Control criteria

- Security records are retained for at least 365 days.
- At least the most recent 90 days are immediately searchable or otherwise readily available.
- The effective logging configuration supports the stated periods.

## Repetition 1

- Verdict: **Conforme** (`compliant`)
- Expected match: **yes**
- Confidence: 1.0
- Retry count: 0; likely truncation: False
- Latency: 474.417 s; prompt/output tokens: 2698/429

- Backend prompt tokens: 2698; independent estimate: 2744

- Prompt processing speed: 9.0 tokens/s; generation speed: 2.5 tokens/s

### Justification

Les paramètres de rétention et de recherche immédiate sont conformes aux exigences du contrôle. Les événements de sécurité sont archivés pendant 400 jours et les 100 derniers jours sont immédiatement recherchables. Les documents d'exploitation et les notes de service confirment que ces paramètres sont appliqués.

### Criterion assessment

- **yes** — Security records are retained for at least 365 days.: Le fichier event-platform-settings.yaml indique que les événements de sécurité sont archivés pendant 400 jours.
- **yes** — At least the most recent 90 days are immediately searchable or otherwise readily available.: Le fichier event-platform-settings.yaml indique que les 100 derniers jours sont immédiatement recherchables.
- **yes** — The effective logging configuration supports the stated periods.: Les documents d'exploitation et les notes de service confirment que les paramètres de rétention et de recherche immédiate sont appliqués.

### Quotes

- ✅ `event-platform-settings.yaml`: retention_days: 400
searchable_days: 100
- ✅ `security-event-handling-standard.md`: Security events are archived for 400 days. The most recent 100 days remain indexed for immediate search.

### Recommendation

Le contrôle est conforme aux exigences. Il est recommandé de maintenir ces paramètres et de vérifier régulièrement leur application.

### Retrieval

- Chunks requested / returned to context: 5 / 5; shortfall: none; tokens sent: 1465
- Retrieval / query embedding: 0.004 s / 3.426 s
- Required gold passages in context: 2/2; all required: True
- Attribution: ok
