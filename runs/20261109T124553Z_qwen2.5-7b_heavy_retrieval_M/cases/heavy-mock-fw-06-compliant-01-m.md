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

- Verdict: **Conforme** (`compliant`)
- Expected match: **yes**
- Confidence: 0.95
- Retry count: 0; likely truncation: False
- Latency: 214.379 s; prompt/output tokens: 2751/463

- Backend prompt tokens: 2751; independent estimate: 2848

- Prompt processing speed: 21.2 tokens/s; generation speed: 5.5 tokens/s

### Justification

Les évidences fournies montrent que les règles d'accès réseau entrant sont limitées aux sources approuvées et aux ports spécifiques. Le pare-feu utilise une stratégie par défaut de refus. Ces aspects correspondent aux critères d'évaluation du contrôle.

### Criterion assessment

- **yes** — No inbound rule allows every source to reach every port.: Les règles d'accès réseau entrant sont spécifiquement définies pour des sources et des ports spécifiques, comme indiqué dans 'perimeter-service-export.yaml'.
- **yes** — Publicly reachable ports are specifically approved and documented.: Les règles d'accès réseau entrant sont spécifiquement définies pour des sources et des ports spécifiques, comme indiqué dans 'perimeter-service-export.yaml'.
- **yes** — A default-deny inbound policy is in effect.: Le fichier 'perimeter-service-export.yaml' montre que la stratégie par défaut est de refuser l'accès, conformément au critère.

### Quotes

- ✅ `network-access-standard-v4.md`: Inbound connections are denied unless a service owner approves a named source and destination port. The perimeter uses a default-deny policy.
- ✅ `perimeter-service-export.yaml`: default_inbound: deny
rules:
- source: 203.0.113.8/32
  port: 443
  action: allow
- source: 198.51.100.0/24
  port: 22
  action: allow


### Recommendation

Le contrôle est conforme aux exigences du mock control.

### Retrieval

- Chunks requested / returned to context: 5 / 5; shortfall: none; tokens sent: 1567
- Retrieval / query embedding: 0.005 s / 0.272 s
- Required gold passages in context: 2/2; all required: True
- Attribution: ok
