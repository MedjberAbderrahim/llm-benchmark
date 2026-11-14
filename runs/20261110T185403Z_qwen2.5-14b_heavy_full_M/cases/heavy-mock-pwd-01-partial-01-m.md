# heavy-mock-pwd-01-partial-01-m

- Control: **MOCK-PWD-01 — Password strength for workforce accounts**
- Expected status: **Partiellement conforme** (`partial`)
- Dataset rationale (human review only): Some safeguards are present, but at least one required scope, threshold, or follow-up condition is missing.
- Language: fr
- Tags: contradiction, heavy, tier_M

## Control criteria

- The enforced minimum password length is at least 14 characters.
- A mix of character types or an equivalent breached-password check is enforced.
- The effective configuration agrees with the written policy.

## Repetition 1

- Verdict: **Partiellement conforme** (`partial`)
- Expected match: **yes**
- Confidence: 0.6
- Retry count: 0; likely truncation: False
- Latency: 678.290 s; prompt/output tokens: 9505/391

- Backend prompt tokens: 5634; independent estimate: 9505

- Prompt processing speed: n/a (cached prefix); generation speed: 2.7 tokens/s

### Justification

The provided documents contain information related to security service registers and benchmark access procedures, but they do not provide a clear and comprehensive overview of the security policies and procedures for all aspects of the system. The documents are specific to certain sections and do not cover all the criteria required for a full compliance assessment.

### Criterion assessment

- **unclear** — Access Control: The documents mention procedures for accessing systems but do not provide a complete overview of the access control policies.
- **yes** — Audit and Accountability: The documents mention the need for traceability and review of access windows, indicating some level of audit and accountability.
- **unclear** — Identification and Authentication: The documents mention identity verification but do not provide a comprehensive overview of the identification and authentication processes.
- **unclear** — Security Assessment and Authorization: The documents do not provide a clear overview of the security assessment and authorization processes.
- **unclear** — Configuration Management: The documents mention service identity management but do not provide a comprehensive overview of the configuration management processes.

### Quotes

- ❌ INVALID `security-policy-5855.md`: La procédure d'accès distant consigne la passerelle autorisée, le contact du support et la trace de revue de chaque fenêtre de maintenance.
- ✅ `platform-change-register-5855.yaml`: lifecycle_state: in-transit

### Recommendation

Further documentation is needed to provide a comprehensive overview of the security policies and procedures for all aspects of the system.
