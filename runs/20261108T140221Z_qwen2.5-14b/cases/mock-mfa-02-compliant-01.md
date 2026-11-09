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
- Latency: 214.265 s; prompt/output tokens: 1184/380

### Justification

Le contrôle est conforme car tous les comptes privilégiés interactifs exigent une authentification à plusieurs facteurs, et les exceptions d'urgence sont documentées et surveillées.

### Criterion assessment

- **yes** — All interactive privileged accounts require MFA.: La configuration active indique que tous les comptes administratifs interactifs exigent une authentification à plusieurs facteurs.
- **yes** — Any emergency account exception is limited, documented, and monitored.: La configuration active indique une exception pour un compte d'urgence, qui est documentée et surveillée.
- **yes** — The active identity configuration agrees with the policy.: La configuration active et la procédure interne concordent sur l'exigence d'une authentification à plusieurs facteurs pour les comptes privilégiés interactifs.

### Quotes

- ✅ `procedure_fr.md`: All interactive privileged users must complete a password and a hardware or app-based second factor. A monitored emergency identity is excluded and reviewed monthly.
- ✅ `effective-config.yaml`: scope: all_interactive_admins
mfa_required: true
exceptions:
- vaulted_emergency_account
emergency_account_monitoring: true

### Recommendation

Aucune recommandation n'est nécessaire car le contrôle est conforme.
