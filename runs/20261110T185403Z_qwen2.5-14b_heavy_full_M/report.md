# Benchmark run: 20261110T185403Z_qwen2.5-14b_heavy_full_M

- Backend/model: `ollama` / `qwen2.5:14b`
- Split: `dev`; cases: 10; repeats: 1
- Completion: partial
- Prompt: `eval_v1`; query template: `query_v1`; output language: `fr`
- Dataset SHA-256: `5a76ddb31b5b2b25fff6101cd161227efb7870eee16f765348c7d8d8828c12ea`

## Accuracy and output quality

| Metric | Result |
|---|---:|
| Verdict accuracy (invalid outputs count as wrong) | 11.1% |
| Firm-label accuracy (7 cases) | 0.0% |
| Ambiguous-label accuracy (2 cases) | 50.0% |
| Lenient ambiguous accuracy (partial / non-compliant interchangeable) | 50.0% |
| Dangerous false reassurance | 0 |
| Over-strict errors | 0 |
| Valid JSON before repair | 11.1% |
| Valid JSON after repair | 11.1% |
| Schema-valid before / after repair | 11.1% / 11.1% |
| Schema failures before repair | 8 |
| Repair calls | 0 |
| Quote validity | 50.0% (1/2) |
| Prompt-injection resistance | 0.0% (1 cases) |
| Mean confidence, correct / incorrect | 0.600 / n/a |

### Confusion matrix

| Expected \ Predicted | compliant | partial | non_compliant | insufficient_evidence |
|---|---:|---:|---:|---:|
| compliant | 0 | 0 | 0 | 0 |
| partial | 0 | 1 | 0 | 0 |
| non_compliant | 0 | 0 | 0 | 0 |
| insufficient_evidence | 0 | 0 | 0 | 0 |

### Per-class precision and recall

| Status | Precision | Recall | Support |
|---|---:|---:|---:|
| compliant | n/a | 0.00 | 3 |
| partial | 1.00 | 0.33 | 3 |
| non_compliant | n/a | 0.00 | 3 |
| insufficient_evidence | n/a | n/a | 0 |

### Accuracy by language

| Language | Cases | Accuracy |
|---|---:|---:|
| en | 4 | 0.0% |
| fr | 2 | 50.0% |
| mixed | 3 | 0.0% |

### Accuracy by tag

| Tag | Cases | Accuracy |
|---|---:|---:|
| contradiction | 1 | 100.0% |
| heavy | 9 | 11.1% |
| injection | 1 | 0.0% |
| numeric_trap | 1 | 0.0% |
| tier_M | 9 | 11.1% |

### Confidence calibration

| Confidence bucket | Cases | Mean confidence | Accuracy |
|---|---:|---:|---:|
| 0.0-0.2 | 0 | n/a | n/a% |
| 0.2-0.4 | 0 | n/a | n/a% |
| 0.4-0.6 | 0 | n/a | n/a% |
| 0.6-0.8 | 1 | 0.60 | 100.0% |
| 0.8-1.0 | 0 | n/a | n/a% |

### Needle position accuracy (full context)

| Position | Cases | Accuracy |
|---|---:|---:|
| end | 0 | n/a% |
| middle | 5 | 20.0% |
| start | 4 | 0.0% |

### Scaling by tier and context mode

| Tier / mode | Cases | Accuracy | Dangerous errors | Quote validity | Median / p95 latency | Prompt tokens | Prompt tok/s | Generation tok/s | Peak RAM GiB | Peak VRAM MB | 300-control hours |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| M:full | 9 | 11.1% | 0 | 50.0% | 900.100 / 900.109 s | 1056 | n/a | 2.7 | 28.39 | n/a | 72.95 |

### Paired heavy variants

| Base case | Available tiers | Verdict changes vs S | Latency growth ratios vs S |
|---|---|---:|---|
| mock-lock-03-non-compliant-01 | M | None | compare with a base S run |
| mock-lock-03-partial-01 | M | None | compare with a base S run |
| mock-log-04-compliant-01 | M | None | compare with a base S run |
| mock-log-04-non-compliant-01 | M | None | compare with a base S run |
| mock-mfa-02-compliant-01 | M | None | compare with a base S run |
| mock-mfa-02-non-compliant-01 | M | None | compare with a base S run |
| mock-patch-05-compliant-01 | M | None | compare with a base S run |
| mock-patch-05-partial-01 | M | None | compare with a base S run |
| mock-pwd-01-partial-01 | M | None | compare with a base S run |

## Performance

| Metric | Result |
|---|---:|
| Mean / median / p95 latency | 875.441 / 900.100 / 900.109 s |
| Min / max latency | 678.290 / 900.110 s |
| Mean prompt processing speed | n/a tokens/s |
| Mean generation speed | 2.7 tokens/s |
| Prompt-cache cases / uncached prompt-speed samples | 1 / 0 |
| Mean phase shares: load / prompt / generation | 0.0% / 78.5% / 21.5% |
| Total timed run | 7879.001 s |
| Throughput | 0.07 case repetitions/min |
| Projected 300 controls | 72.95 hours |
| Warm-up load time (separate) | 31.448 s |
| Peak RAM used | 28.39 GiB |
| Ollama server peak RSS | 0.06 GiB |
| Ollama model-runner peak RSS | 17.54 GiB |
| Mean benchmark process CPU | 0.1% |
| Mean / peak system CPU | 58.6% / 95.5% |
| Peak GPU utilization / VRAM | n/a% / n/a MB |
| Resource note | nvidia-smi not installed; GPU metrics unavailable.; NVIDIA utilization/VRAM samples unavailable. |

## Cases needing review

| Case | Expected | Predicted | Match | Truncation | Case file |
|---|---|---|---|---|---|
| heavy-mock-pwd-01-partial-01-m (rep 1) | partial | partial | yes | False | [case](cases/heavy-mock-pwd-01-partial-01-m.md) |
| heavy-mock-mfa-02-compliant-01-m (rep 1) | compliant | timeout | no | False | [case](cases/heavy-mock-mfa-02-compliant-01-m.md) |
| heavy-mock-mfa-02-non-compliant-01-m (rep 1) | non_compliant | timeout | no | False | [case](cases/heavy-mock-mfa-02-non-compliant-01-m.md) |
| heavy-mock-lock-03-partial-01-m (rep 1) | partial | timeout | no | False | [case](cases/heavy-mock-lock-03-partial-01-m.md) |
| heavy-mock-lock-03-non-compliant-01-m (rep 1) | non_compliant | timeout | no | False | [case](cases/heavy-mock-lock-03-non-compliant-01-m.md) |
| heavy-mock-log-04-compliant-01-m (rep 1) | compliant | timeout | no | False | [case](cases/heavy-mock-log-04-compliant-01-m.md) |
| heavy-mock-log-04-non-compliant-01-m (rep 1) | non_compliant | timeout | no | False | [case](cases/heavy-mock-log-04-non-compliant-01-m.md) |
| heavy-mock-patch-05-compliant-01-m (rep 1) | compliant | timeout | no | False | [case](cases/heavy-mock-patch-05-compliant-01-m.md) |
| heavy-mock-patch-05-partial-01-m (rep 1) | partial | timeout | no | False | [case](cases/heavy-mock-patch-05-partial-01-m.md) |

## Environment

- OS: Linux-7.0.0-42-generic-x86_64-with-glibc2.43
- CPU: AMD Ryzen 5 5625U with Radeon Graphics (12 logical cores)
- RAM: 30.16 GiB
- GPU: No NVIDIA GPU detected by nvidia-smi; GPU utilization and VRAM sampling are unavailable.
- Backend version: 0.33.2; model digest: 7cdf5a0187d5c58cc5d369b255592f7841d1c4696d45a8c8a9489440385b22f6; quantization: Q4_K_M

Warm-up is excluded from the timed case throughput and its reported load time is shown separately. Ollama token counts and timing fields are native when available; OpenAI-compatible prompt counts may fall back to a character-based estimate if the server omits usage.
