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

- Verdict: **Non conforme** (`non_compliant`)
- Expected match: **no**
- Confidence: 0.85
- Retry count: 0; likely truncation: False
- Latency: 335.703 s; prompt/output tokens: 9505/494

- Backend prompt tokens: 5634; independent estimate: 9505

- Prompt processing speed: n/a (cached prefix); generation speed: 5.5 tokens/s

### Justification

The evaluation found that the criteria for the 'Access Management' section were not fully met. Specifically, the document does not provide clear evidence that all access requests are properly authorized, documented, and reviewed. Additionally, the document does not specify the process for revoking access when a service is decommissioned, which is a critical aspect of access management.

### Criterion assessment

- **no** — All access requests are properly authorized, documented, and reviewed.: The document does not provide clear evidence of this process.
- **no** — Access is revoked when a service is decommissioned.: The document does not specify the process for revoking access.

### Quotes

- ❌ INVALID `platform-access-management-5854.yaml`: La procédure d'accès distant consigne la passerelle autorisée, le contact du support et la trace de revue de chaque fenêtre de maintenance.
- ❌ INVALID `platform-access-management-5854.yaml`: Les identités de service sont attribuées à une équipe propriétaire, inscrites à l'inventaire et retirées par le processus de changement lorsqu'une charge est arrêtée.
- ❌ INVALID `platform-access-management-5854.yaml`: Les demandes de réinitialisation au support exigent une vérification d'identité consignée, un responsable de ticket et une confirmation de reprise d'accès.
- ❌ INVALID `platform-access-management-5854.yaml`: Les clés privées SSH restent auprès de leurs dépositaires désignés; les transferts sont documentés sans copier de secret dans le registre de service.

### Recommendation

The organization should establish and document a clear process for authorizing, documenting, and reviewing access requests. Additionally, a process for revoking access when a service is decommissioned should be defined and implemented.
