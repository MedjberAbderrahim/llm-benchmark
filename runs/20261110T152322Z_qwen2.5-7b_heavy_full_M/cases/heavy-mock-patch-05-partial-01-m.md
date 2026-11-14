# heavy-mock-patch-05-partial-01-m

- Control: **MOCK-PATCH-05 — Timely critical security updates**
- Expected status: **Partiellement conforme** (`partial`)
- Dataset rationale (human review only): Some safeguards are present, but at least one required scope, threshold, or follow-up condition is missing.
- Language: en
- Tags: heavy, tier_M

## Control criteria

- Critical security updates are deployed within 30 calendar days of release or identification.
- The deadline applies to in-scope production systems.
- Records show due dates and completion or tracked exceptions.

## Repetition 1

- Verdict: **Partiellement conforme** (`partial`)
- Expected match: **yes**
- Confidence: 0.8
- Retry count: 0; likely truncation: True
- Latency: 775.339 s; prompt/output tokens: 10167/436

- Backend prompt tokens: 10167; independent estimate: 9537

- Prompt processing speed: 15.5 tokens/s; generation speed: 3.7 tokens/s

### Justification

The evidence indicates that critical security updates are deployed within 45 days, which is longer than the 30-day requirement. However, the evidence does not show that all critical updates are deployed within 30 days. The policy states that exceptions are discussed at the monthly meeting, but there is no evidence of such discussions or exceptions being tracked. The deployment service export shows that some assets are in a staged or retired state, which may indicate that not all critical updates are being applied in a timely manner.

### Criterion assessment

- **no** — Critical security updates are deployed within 30 calendar days of release or identification.: The critical_deadline_days in the deployment-service-export.yaml is set to 45 days, which is longer than the required 30 days.
- **yes** — The deadline applies to in-scope production systems.: The scope in the deployment-service-export.yaml is set to production_servers, indicating that the deadline applies to in-scope production systems.
- **no** — Records show due dates and completion or tracked exceptions.: There is no evidence of due dates, completion, or tracked exceptions in the provided evidence.

### Quotes

- ✅ `deployment-service-export.yaml`: critical_deadline_days: 45
- ✅ `change-management-standard-v4.md`: Critical updates should be installed within 45 days when operations allow. Exceptions are discussed at the monthly meeting.

### Recommendation

Implement a more stringent timeline for critical security updates, ideally within 30 days. Ensure that all critical updates are tracked and documented, and that exceptions are formally discussed and recorded at the monthly meeting.
