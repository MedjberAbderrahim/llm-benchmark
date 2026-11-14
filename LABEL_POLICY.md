# Draft label policy: partial versus non-compliant

**Status: proposal for review by a qualified auditor. The rule choice is pending.** The existing base labels and their hash are unchanged. The two rules below describe different conventions; the benchmark should not treat either as authoritative until the auditor approves one.

## Candidate rules

- **R1 — strict all criteria:** compliant only when every criterion is met; partial when at least one criterion is clearly met and at least one is unmet or not demonstrated; non-compliant when none is met. Use insufficient evidence when no criterion can be assessed.
- **R2 — core criterion:** the control owner designates a core criterion for each control. If the core criterion is unmet, classify non-compliant. Classify partial only when the core is met and one or more secondary criteria are unmet. Use insufficient evidence when the core cannot be assessed.

## Effect on flagged base cases

| Case | R1 likely result | R2 likely result | Review note |
|---|---|---|---|
| `mock-pwd-01-partial-01` | partial | non-compliant | Complexity is present, but the 8-character effective setting misses the 14-character core threshold and conflicts with the written 12-character statement. |
| `mock-tls-07-partial-01` | partial if the main endpoint is treated as an assessed in-scope service; otherwise insufficient evidence | insufficient evidence if all-public-endpoint coverage is the core | The evidence covers the main portal, but does not inventory the historical service. The current label is ambiguous and likely overstated. |
| `mock-lock-03-partial-01` | partial | non-compliant | A protective lock exists, but the 8-failure threshold and 10-minute duration miss both stated numeric conditions; the first threshold is the proposed core. |
| `mock-mfa-02-partial-01` | partial | non-compliant | Remote administration is protected, while local console access remains outside coverage; all interactive privileged access is the proposed core. |
| `mock-access-08-partial-01` | partial | non-compliant | Some review and action tracking is evidenced, but semiannual timing misses the proposed 90-day core and population coverage is unclear. |

The candidate core criteria in this table are suggested only to expose the effect of R2. The auditor should confirm or replace them. `data/label_flags.yaml` records these five cases as `ambiguous`; every other base case is marked `firm`. Heavy paired cases inherit that confidence flag, while designed adversarial cases are marked firm.
