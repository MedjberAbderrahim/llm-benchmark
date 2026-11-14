# Benchmark run: 20261110T152322Z_qwen2.5-7b_heavy_full_M

- Backend/model: `ollama` / `qwen2.5:7b`
- Split: `dev`; cases: 10; repeats: 1
- Completion: complete
- Prompt: `eval_v1`; query template: `query_v1`; output language: `fr`
- Dataset SHA-256: `5a76ddb31b5b2b25fff6101cd161227efb7870eee16f765348c7d8d8828c12ea`

## Accuracy and output quality

| Metric | Result |
|---|---:|
| Verdict accuracy (invalid outputs count as wrong) | 70.0% |
| Firm-label accuracy (8 cases) | 87.5% |
| Ambiguous-label accuracy (2 cases) | 0.0% |
| Lenient ambiguous accuracy (partial / non-compliant interchangeable) | 100.0% |
| Dangerous false reassurance | 0 |
| Over-strict errors | 2 |
| Valid JSON before repair | 90.0% |
| Valid JSON after repair | 90.0% |
| Schema-valid before / after repair | 90.0% / 90.0% |
| Schema failures before repair | 1 |
| Repair calls | 1 |
| Quote validity | 78.9% (15/19) |
| Prompt-injection resistance | 100.0% (1 cases) |
| Mean confidence, correct / incorrect | 0.936 / 0.875 |

### Confusion matrix

| Expected \ Predicted | compliant | partial | non_compliant | insufficient_evidence |
|---|---:|---:|---:|---:|
| compliant | 3 | 0 | 0 | 0 |
| partial | 0 | 1 | 2 | 0 |
| non_compliant | 0 | 0 | 3 | 0 |
| insufficient_evidence | 0 | 0 | 0 | 0 |

### Per-class precision and recall

| Status | Precision | Recall | Support |
|---|---:|---:|---:|
| compliant | 1.00 | 0.75 | 4 |
| partial | 1.00 | 0.33 | 3 |
| non_compliant | 0.60 | 1.00 | 3 |
| insufficient_evidence | n/a | n/a | 0 |

### Accuracy by language

| Language | Cases | Accuracy |
|---|---:|---:|
| en | 5 | 100.0% |
| fr | 2 | 0.0% |
| mixed | 3 | 66.7% |

### Accuracy by tag

| Tag | Cases | Accuracy |
|---|---:|---:|
| contradiction | 1 | 0.0% |
| distractor | 1 | 100.0% |
| heavy | 10 | 70.0% |
| injection | 1 | 100.0% |
| numeric_trap | 1 | 100.0% |
| tier_M | 10 | 70.0% |

### Confidence calibration

| Confidence bucket | Cases | Mean confidence | Accuracy |
|---|---:|---:|---:|
| 0.0-0.2 | 0 | n/a | n/a% |
| 0.2-0.4 | 0 | n/a | n/a% |
| 0.4-0.6 | 0 | n/a | n/a% |
| 0.6-0.8 | 0 | n/a | n/a% |
| 0.8-1.0 | 9 | 0.92 | 77.8% |

### Needle position accuracy (full context)

| Position | Cases | Accuracy |
|---|---:|---:|
| end | 0 | n/a% |
| middle | 5 | 60.0% |
| start | 5 | 80.0% |

### Scaling by tier and context mode

| Tier / mode | Cases | Accuracy | Dangerous errors | Quote validity | Median / p95 latency | Prompt tokens | Prompt tok/s | Generation tok/s | Peak RAM GiB | Peak VRAM MB | 300-control hours |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| M:full | 10 | 70.0% | 0 | 78.9% | 761.277 / 794.303 s | 9947 | 16.3 | 4.0 | 18.04 | n/a | 55.50 |

### Paired heavy variants

| Base case | Available tiers | Verdict changes vs S | Latency growth ratios vs S |
|---|---|---:|---|
| mock-fw-06-compliant-01 | M | None | compare with a base S run |
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
| Mean / median / p95 latency | 665.977 / 761.277 / 794.303 s |
| Min / max latency | 335.703 / 797.113 s |
| Mean prompt processing speed | 16.3 tokens/s |
| Mean generation speed | 4.0 tokens/s |
| Prompt-cache cases / uncached prompt-speed samples | 2 / 8 |
| Mean phase shares: load / prompt / generation | 0.0% / 81.7% / 18.2% |
| Total timed run | 6659.867 s |
| Throughput | 0.09 case repetitions/min |
| Projected 300 controls | 55.50 hours |
| Warm-up load time (separate) | 14.224 s |
| Peak RAM used | 18.04 GiB |
| Ollama server peak RSS | 0.06 GiB |
| Ollama model-runner peak RSS | 10.04 GiB |
| Mean benchmark process CPU | 0.1% |
| Mean / peak system CPU | 55.1% / 93.5% |
| Peak GPU utilization / VRAM | n/a% / n/a MB |
| Resource note | nvidia-smi not installed; GPU metrics unavailable.; NVIDIA utilization/VRAM samples unavailable. |

## Cases needing review

| Case | Expected | Predicted | Match | Truncation | Case file |
|---|---|---|---|---|---|
| heavy-mock-pwd-01-partial-01-m (rep 1) | partial | non_compliant | no | False | [case](cases/heavy-mock-pwd-01-partial-01-m.md) |
| heavy-mock-mfa-02-compliant-01-m (rep 1) | compliant | invalid_output | no | False | [case](cases/heavy-mock-mfa-02-compliant-01-m.md) |
| heavy-mock-lock-03-partial-01-m (rep 1) | partial | non_compliant | no | True | [case](cases/heavy-mock-lock-03-partial-01-m.md) |
| heavy-mock-lock-03-non-compliant-01-m (rep 1) | non_compliant | non_compliant | yes | True | [case](cases/heavy-mock-lock-03-non-compliant-01-m.md) |
| heavy-mock-log-04-non-compliant-01-m (rep 1) | non_compliant | non_compliant | yes | True | [case](cases/heavy-mock-log-04-non-compliant-01-m.md) |
| heavy-mock-patch-05-compliant-01-m (rep 1) | compliant | compliant | yes | True | [case](cases/heavy-mock-patch-05-compliant-01-m.md) |
| heavy-mock-patch-05-partial-01-m (rep 1) | partial | partial | yes | True | [case](cases/heavy-mock-patch-05-partial-01-m.md) |

## Environment

- OS: Linux-7.0.0-42-generic-x86_64-with-glibc2.43
- CPU: AMD Ryzen 5 5625U with Radeon Graphics (12 logical cores)
- RAM: 30.16 GiB
- GPU: No NVIDIA GPU detected by nvidia-smi; GPU utilization and VRAM sampling are unavailable.
- Backend version: 0.33.2; model digest: 845dbda0ea48ed749caafd9e6037047aa19acfcfd82e704d7ca97d631a0b697e; quantization: Q4_K_M

Warm-up is excluded from the timed case throughput and its reported load time is shown separately. Ollama token counts and timing fields are native when available; OpenAI-compatible prompt counts may fall back to a character-based estimate if the server omits usage.
