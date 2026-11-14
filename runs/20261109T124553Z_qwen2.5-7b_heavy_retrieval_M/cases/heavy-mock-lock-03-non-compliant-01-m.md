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
- Confidence: 0.9
- Retry count: 0; likely truncation: False
- Latency: 242.499 s; prompt/output tokens: 3300/467

- Backend prompt tokens: 3300; independent estimate: 3285

- Prompt processing speed: 21.4 tokens/s; generation speed: 5.3 tokens/s

### Justification

Les preuves fournies montrent que l'authentification ne bloque pas les comptes après des tentatives de connexion infructueuses. Les paramètres configurés indiquent que l'authentification ne bloque pas les comptes après des tentatives de connexion infructueuses et que l'état de verrouillage ne dure pas. Les procédures internes ne contiennent aucune indication contraire.

### Criterion assessment

- **no** — Accounts are blocked or delayed after no more than 5 consecutive failures.: Le fichier 'authentication-export.json' montre que 'failed_attempt_threshold' est 0 et 'lockout_enabled' est false, indiquant que les comptes ne sont pas verrouillés après des tentatives de connexion infructueuses.
- **no** — The protective state lasts at least 15 minutes or requires an approved reset.: Les preuves fournies ne contiennent aucune indication sur la durée du verrouillage ou la nécessité d'un reset approuvé.
- **no** — The configured behavior is evidenced.: Les procédures internes ne contiennent aucune indication sur la configuration effective de la gestion des tentatives de connexion infructueuses.

### Quotes

- ✅ `authentication-export.json`: "failed_attempt_threshold": 0, "lockout_enabled": false
- ✅ `authentication-operations-standard.md`: Accounts remain available after failed sign-ins. Monitoring alerts are reviewed during business hours.

### Recommendation

Recommander la mise en œuvre d'une stratégie de gestion des tentatives de connexion infructueuses qui bloque temporairement les comptes après un certain nombre de tentatives échouées.

### Retrieval

- Chunks requested / returned to context: 5 / 5; shortfall: none; tokens sent: 1940
- Retrieval / query embedding: 0.006 s / 0.300 s
- Required gold passages in context: 2/2; all required: True
- Attribution: ok
