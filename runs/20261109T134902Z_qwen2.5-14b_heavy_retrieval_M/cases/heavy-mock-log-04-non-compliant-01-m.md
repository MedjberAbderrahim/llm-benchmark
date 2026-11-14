# heavy-mock-log-04-non-compliant-01-m

- Control: **MOCK-LOG-04 — Security event retention and availability**
- Expected status: **Non conforme** (`non_compliant`)
- Dataset rationale (human review only): The effective evidence shows a material failure against one or more required criteria.
- Language: en
- Tags: numeric_trap, heavy, tier_M

## Control criteria

- Security records are retained for at least 365 days.
- At least the most recent 90 days are immediately searchable or otherwise readily available.
- The effective logging configuration supports the stated periods.

## Repetition 1

- Verdict: **Non conforme** (`non_compliant`)
- Expected match: **yes**
- Confidence: 1.0
- Retry count: 0; likely truncation: False
- Latency: 558.013 s; prompt/output tokens: 3365/487

- Backend prompt tokens: 3365; independent estimate: 3187

- Prompt processing speed: 9.4 tokens/s; generation speed: 2.4 tokens/s

### Justification

Le contrôle évalue que les journaux de sécurité doivent être conservés pendant au moins 365 jours et que les 90 derniers jours doivent être immédiatement recherchables ou autrement facilement disponibles. Les preuves fournies indiquent que les journaux de sécurité sont conservés pendant 90 jours au total et que les 30 derniers jours sont consultables rapidement. Cela ne respecte pas les exigences du contrôle.

### Criterion assessment

- **no** — Security records are retained for at least 365 days.: Les journaux de sécurité sont conservés pendant 90 jours au total, ce qui est inférieur à la période minimale requise de 365 jours.
- **no** — At least the most recent 90 days are immediately searchable or otherwise readily available.: Les 30 derniers jours sont consultables rapidement, ce qui est inférieur à la période minimale requise de 90 jours.
- **no** — The effective logging configuration supports the stated periods.: La configuration de journalisation effective ne prend pas en charge les périodes de conservation et de disponibilité requises.

### Quotes

- ✅ `collector-settings.ini`: [effective_policy]
retention_days = 90
searchable_days = 30
- ✅ `security-event-handling-standard.md`: Les journaux de sécurité sont conservés pendant 90 jours au total. Les 30 jours les plus récents sont consultables rapidement.

### Recommendation

Il est recommandé de mettre à jour la configuration de conservation des journaux de sécurité pour respecter les exigences du contrôle, à savoir une conservation de 365 jours et une disponibilité immédiate des 90 derniers jours.

### Retrieval

- Chunks requested / returned to context: 5 / 5; shortfall: none; tokens sent: 1884
- Retrieval / query embedding: 0.005 s / 3.513 s
- Required gold passages in context: 2/2; all required: True
- Attribution: ok
