# heavy-mock-patch-05-compliant-01-m

- Control: **MOCK-PATCH-05 — Timely critical security updates**
- Expected status: **Conforme** (`compliant`)
- Dataset rationale (human review only): The cited policy and effective export satisfy the stated mock criteria.
- Language: en
- Tags: heavy, tier_M

## Control criteria

- Critical security updates are deployed within 30 calendar days of release or identification.
- The deadline applies to in-scope production systems.
- Records show due dates and completion or tracked exceptions.

## Repetition 1

- Verdict: **Conforme** (`compliant`)
- Expected match: **yes**
- Confidence: 0.95
- Retry count: 0; likely truncation: True
- Latency: 797.113 s; prompt/output tokens: 10607/364

- Backend prompt tokens: 10607; independent estimate: 9592

- Prompt processing speed: 15.4 tokens/s; generation speed: 3.4 tokens/s

### Justification

The evidence provided shows that critical security updates are deployed within 20 calendar days of identification, which is within the 30-day requirement stated in the control. The asset update register and change management standard both confirm this timeline. The service continuity plan and supplier coordination notes also support the process and records.

### Criterion assessment

- **yes** — Critical security updates are deployed within 30 calendar days of release or identification.: The asset update register specifies a 20-day deadline, which is within the 30-day requirement.
- **yes** — The deadline applies to in-scope production systems.: The change management standard specifies that the procedure applies to production assets.
- **yes** — Records show due dates and completion or tracked exceptions.: The asset update register includes fields for 'identified_at', 'due_at', and 'deployed_at', and the change management standard confirms that these records are maintained.

### Quotes

- ✅ `change-management-standard-v4.md`: Critical fixes for production assets are due within 20 calendar days.
- ✅ `asset-update-register.json`: "critical_deadline_days": 20

### Recommendation

Maintain the current process and ensure continued adherence to the 20-day deadline for critical security updates.
