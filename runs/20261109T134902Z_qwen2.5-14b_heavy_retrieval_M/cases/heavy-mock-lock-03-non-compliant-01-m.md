# heavy-mock-lock-03-non-compliant-01-m

- Control: **MOCK-LOCK-03 — Repeated sign-in failure handling**
- Expected status: **Non conforme** (`non_compliant`)
- Dataset rationale (human review only): The effective evidence shows a material failure against one or more required criteria.
- Language: en
- Tags: heavy, tier_M

## Control criteria

- Accounts are blocked or delayed after no more than 5 consecutive failures.
- The protective state lasts at least 15 minutes or requires an approved reset.
- The configured behavior is evidenced.

## Repetition 1

- Verdict: **Non conforme** (`non_compliant`)
- Expected match: **yes**
- Confidence: 1.0
- Retry count: 0; likely truncation: False
- Latency: 603.993 s; prompt/output tokens: 3300/474

- Backend prompt tokens: 3300; independent estimate: 3285

- Prompt processing speed: 8.3 tokens/s; generation speed: 2.3 tokens/s

### Justification

Le contrôle évalue la réaction en cas de tentatives de connexion infructueuses répétées. Les preuves montrent que les tentatives de connexion infructueuses ne déclenchent pas de blocage ou de délai des comptes, et que les comptes restent disponibles après des tentatives infructueuses. Les paramètres configurés indiquent que le seuil de tentatives infructueuses est de 0 et que le verrouillage est désactivé.

### Criterion assessment

- **no** — Accounts are blocked or delayed after no more than 5 consecutive failures.: Le paramètre failed_attempt_threshold est défini à 0 et lockout_enabled est défini à false, ce qui signifie que les comptes ne sont pas verrouillés après un certain nombre de tentatives infructueuses.
- **no** — The protective state lasts at least 15 minutes or requires an approved reset.: Comme le verrouillage est désactivé, il n'y a pas d'état protecteur qui dure au moins 15 minutes.
- **yes** — The configured behavior is evidenced.: Les preuves montrent que le verrouillage est désactivé et que le seuil de tentatives infructueuses est de 0.

### Quotes

- ✅ `authentication-export.json`:   "failed_attempt_threshold": 0,
  "lockout_enabled": false,
- ✅ `authentication-operations-standard.md`: Accounts remain available after failed sign-ins. Monitoring alerts are reviewed during business hours.

### Recommendation

Il est recommandé de configurer un seuil de tentatives infructueuses et d'activer le verrouillage pour répondre aux exigences du contrôle.

### Retrieval

- Chunks requested / returned to context: 5 / 5; shortfall: none; tokens sent: 1940
- Retrieval / query embedding: 0.004 s / 3.168 s
- Required gold passages in context: 2/2; all required: True
- Attribution: ok
