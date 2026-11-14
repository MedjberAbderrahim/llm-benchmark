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
- Confidence: 0.85
- Retry count: 0; likely truncation: False
- Latency: 204.555 s; prompt/output tokens: 2690/407

- Backend prompt tokens: 2690; independent estimate: 2775

- Prompt processing speed: 20.5 tokens/s; generation speed: 5.6 tokens/s

### Justification

The evidence indicates that critical updates are deployed within 45 days, which is longer than the 30 days required by the control. While the policy is documented, the actual deployment timeline does not meet the control's requirement. The evidence also shows that exceptions are discussed at monthly meetings, which is a good practice but does not fully address the control's requirement for timely deployment.

### Criterion assessment

- **no** — Critical security updates are deployed within 30 calendar days of release or identification.: The evidence shows a 45-day deadline for critical updates, which exceeds the 30-day requirement.
- **yes** — The deadline applies to in-scope production systems.: The evidence specifies that the scope is production servers, indicating that the deadline applies to in-scope production systems.
- **yes** — Records show due dates and completion or tracked exceptions.: The evidence indicates that exceptions are tracked and discussed at monthly meetings, and that records are maintained for due dates and completion.

### Quotes

- ✅ `change-management-standard-v4.md`: Critical updates should be installed within 45 days when operations allow. Exceptions are discussed at the monthly meeting.
- ✅ `deployment-service-export.yaml`: critical_deadline_days: 45

### Recommendation

The organization should revise its patch management procedure to ensure that critical security updates are deployed within 30 days of release or identification. This can be achieved by implementing stricter deadlines and possibly automating the update process.

### Retrieval

- Chunks requested / returned to context: 5 / 5; shortfall: none; tokens sent: 1477
- Retrieval / query embedding: 0.006 s / 0.332 s
- Required gold passages in context: 2/2; all required: True
- Attribution: ok
