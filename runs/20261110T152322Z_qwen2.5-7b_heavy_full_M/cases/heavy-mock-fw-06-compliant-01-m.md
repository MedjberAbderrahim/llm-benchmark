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
- Confidence: 1.0
- Retry count: 0; likely truncation: False
- Latency: 622.730 s; prompt/output tokens: 9263/392

- Backend prompt tokens: 9263; independent estimate: 9524

- Prompt processing speed: 17.7 tokens/s; generation speed: 4.0 tokens/s

### Justification

The evidence provided shows that the network perimeter uses a default-deny policy, and only specific sources are allowed access to certain ports. The procedure document explicitly states that inbound connections are denied unless a service owner approves a named source and destination port. The current inbound ruleset export also aligns with the policy of denying all inbound traffic by default and allowing only specific sources.

### Criterion assessment

- **yes** — No inbound rule allows every source to reach every port.: The current inbound ruleset export shows that only specific sources are allowed access to certain ports, and there are no rules allowing every source to reach every port.
- **yes** — Publicly reachable ports are specifically approved and documented.: The current inbound ruleset export lists specific sources and ports that are allowed, indicating that publicly reachable ports are specifically approved and documented.
- **yes** — A default-deny inbound policy is in effect.: The current inbound ruleset export and the procedure document both indicate that a default-deny inbound policy is in effect.

### Quotes

- ✅ `perimeter-service-export.yaml`: default_inbound: deny
- ✅ `network-access-standard-v4.md`: Inbound connections are denied unless a service owner approves a named source and destination port. The perimeter uses a default-deny policy.

### Recommendation

Maintain the current configuration and ensure that all future changes are documented and approved according to the established procedure.
