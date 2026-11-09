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
- Latency: 85.530 s; prompt/output tokens: 1220/304

- Backend prompt tokens: 1220; independent estimate: 1287

- Prompt processing speed: 27.5 tokens/s; generation speed: 7.4 tokens/s

### Justification

The evidence shows that all interactive privileged accounts require MFA, and the emergency account exception is limited, documented, and monitored. The active identity configuration agrees with the policy.

### Criterion assessment

- **yes** — All interactive privileged accounts require MFA.: The `effective-config.yaml` file states `mfa_required: true` for all interactive admins.
- **yes** — Any emergency account exception is limited, documented, and monitored.: The `effective-config.yaml` file lists an exception for `vaulted_emergency_account` and states `emergency_account_monitoring: true`.
- **yes** — The active identity configuration agrees with the policy.: The `effective-config.yaml` file's configuration aligns with the policy requirements.

### Quotes

- ✅ `effective-config.yaml`: mfa_required: true
- ✅ `effective-config.yaml`: emergency_account_monitoring: true

### Recommendation

Maintain current MFA configuration and continue monitoring emergency account exceptions.
