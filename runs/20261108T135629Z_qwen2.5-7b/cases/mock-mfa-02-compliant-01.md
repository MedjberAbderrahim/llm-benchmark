# mock-mfa-02-compliant-01

- Control: **MOCK-MFA-02 — Multi-factor authentication for administrators**
- Expected status: **Conforme** (`compliant`)
- Dataset rationale (human review only): The cited policy and effective export satisfy the stated mock criteria.
- Language: fr
- Tags: none

## Control criteria

- All interactive privileged accounts require MFA.
- Any emergency account exception is limited, documented, and monitored.
- The active identity configuration agrees with the policy.

## Repetition 1

- Verdict: **Conforme** (`compliant`)
- Expected match: **yes**
- Confidence: 1.0
- Retry count: 0; likely truncation: False
- Latency: 41.978 s; prompt/output tokens: 1184/293

### Justification

The evidence shows that all interactive privileged accounts require MFA, and the emergency account exception is documented and monitored, aligning with the control requirements.

### Criterion assessment

- **yes** — All interactive privileged accounts require MFA.: The effective-config.yaml file explicitly states that MFA is required for all interactive privileged users.
- **yes** — Any emergency account exception is limited, documented, and monitored.: The effective-config.yaml file lists an emergency account exception and specifies that monitoring is in place.
- **yes** — The active identity configuration agrees with the policy.: The procedure_fr.md document and the effective-config.yaml file both indicate that the policy is being followed.

### Quotes

- ✅ `effective-config.yaml`: mfa_required: true
- ✅ `effective-config.yaml`: emergency_account_monitoring: true

### Recommendation

Maintain the current MFA configuration and continue to monitor the emergency account exception.
