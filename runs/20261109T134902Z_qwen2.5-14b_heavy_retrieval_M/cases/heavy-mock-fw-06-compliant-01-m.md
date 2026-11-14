# heavy-mock-fw-06-compliant-01-m

- Control: **MOCK-FW-06 — Restrictive inbound network rules**
- Expected status: **Conforme** (`compliant`)
- Dataset rationale (human review only): The cited policy and effective export satisfy the stated mock criteria.
- Language: en
- Tags: distractor, heavy, tier_M

## Control criteria

- No inbound rule allows every source to reach every port.
- Publicly reachable ports are specifically approved and documented.
- A default-deny inbound policy is in effect.

## Repetition 1

- Verdict: **Partiellement conforme** (`partial`)
- Expected match: **no**
- Confidence: 0.8
- Retry count: 0; likely truncation: False
- Latency: 413.758 s; prompt/output tokens: 2752/439

- Backend prompt tokens: 2752; independent estimate: 2848

- Prompt processing speed: 10.2 tokens/s; generation speed: 3.1 tokens/s

### Justification

Le contrôle évalue la conformité des règles de pare-feu entrantes. Les preuves montrent une politique de défaut de refus pour les connexions entrantes et des règles spécifiques approuvées pour des sources et des ports spécifiques. Cependant, il n'y a pas de preuve claire que les ports publics sont spécifiquement approuvés et documentés.

### Criterion assessment

- **yes** — No inbound rule allows every source to reach every port.: Le fichier 'perimeter-service-export.yaml' montre que les règles d'accès entrant sont spécifiques et ne permettent pas à toute source d'accéder à tous les ports.
- **unclear** — Publicly reachable ports are specifically approved and documented.: Il n'y a pas de preuve claire dans les extraits fournis que les ports publics sont spécifiquement approuvés et documentés.
- **yes** — A default-deny inbound policy is in effect.: Le fichier 'perimeter-service-export.yaml' indique que la politique par défaut pour les connexions entrantes est 'deny'.

### Quotes

- ✅ `network-access-standard-v4.md`: Inbound connections are denied unless a service owner approves a named source and destination port. The perimeter uses a default-deny policy.
- ✅ `perimeter-service-export.yaml`: default_inbound: deny

### Recommendation

Il est recommandé de vérifier et de documenter spécifiquement les ports publics qui sont approuvés et utilisés.

### Retrieval

- Chunks requested / returned to context: 5 / 5; shortfall: none; tokens sent: 1567
- Retrieval / query embedding: 0.007 s / 3.419 s
- Required gold passages in context: 2/2; all required: True
- Attribution: llm_error
