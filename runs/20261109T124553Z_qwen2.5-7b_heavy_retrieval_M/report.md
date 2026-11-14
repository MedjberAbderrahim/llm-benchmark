# Benchmark run: 20261109T124553Z_qwen2.5-7b_heavy_retrieval_M

- Backend/model: `ollama` / `qwen2.5:7b`
- Split: `dev`; cases: 10; repeats: 1
- Completion: complete
- Prompt: `eval_v2_retrieval`; query template: `query_v1`; output language: `fr`
- Dataset SHA-256: `5a76ddb31b5b2b25fff6101cd161227efb7870eee16f765348c7d8d8828c12ea`

## Accuracy and output quality

| Metric                                                               |           Result |
| -------------------------------------------------------------------- | ---------------: |
| Verdict accuracy (invalid outputs count as wrong)                    |            60.0% |
| Firm-label accuracy (8 cases)                                        |            62.5% |
| Ambiguous-label accuracy (2 cases)                                   |            50.0% |
| Lenient ambiguous accuracy (partial / non-compliant interchangeable) |           100.0% |
| Dangerous false reassurance                                          |                0 |
| Over-strict errors                                                   |                3 |
| Valid JSON before repair                                             |            90.0% |
| Valid JSON after repair                                              |            90.0% |
| Schema-valid before / after repair                                   |    90.0% / 90.0% |
| Schema failures before repair                                        |                1 |
| Repair calls                                                         |                1 |
| Quote validity                                                       |    93.8% (15/16) |
| Prompt-injection resistance                                          | 100.0% (1 cases) |
| Mean confidence, correct / incorrect                                 |    0.900 / 0.833 |

### Confusion matrix

| Expected \ Predicted | compliant | partial | non_compliant | insufficient_evidence |
|---|---:|---:|---:|---:|
| compliant | 2 | 1 | 1 | 0 |
| partial | 0 | 2 | 1 | 0 |
| non_compliant | 0 | 0 | 2 | 0 |
| insufficient_evidence | 0 | 0 | 0 | 0 |

### Per-class precision and recall

| Status | Precision | Recall | Support |
|---|---:|---:|---:|
| compliant | 1.00 | 0.50 | 4 |
| partial | 0.67 | 0.67 | 3 |
| non_compliant | 0.50 | 0.67 | 3 |
| insufficient_evidence | n/a | n/a | 0 |

### Accuracy by language

| Language | Cases | Accuracy |
|---|---:|---:|
| en | 5 | 60.0% |
| fr | 2 | 0.0% |
| mixed | 3 | 100.0% |

### Accuracy by tag

| Tag | Cases | Accuracy |
|---|---:|---:|
| contradiction | 1 | 0.0% |
| distractor | 1 | 100.0% |
| heavy | 10 | 60.0% |
| injection | 1 | 100.0% |
| numeric_trap | 1 | 0.0% |
| tier_M | 10 | 60.0% |

### Confidence calibration

| Confidence bucket | Cases | Mean confidence | Accuracy |
|---|---:|---:|---:|
| 0.0-0.2 | 0 | n/a | n/a% |
| 0.2-0.4 | 0 | n/a | n/a% |
| 0.4-0.6 | 0 | n/a | n/a% |
| 0.6-0.8 | 0 | n/a | n/a% |
| 0.8-1.0 | 9 | 0.88 | 66.7% |

### Needle position accuracy (full context)

| Position | Cases | Accuracy |
|---|---:|---:|
| end | 0 | n/a% |
| middle | 0 | n/a% |
| start | 0 | n/a% |

### Scaling by tier and context mode

| Tier / mode | Cases | Accuracy | Dangerous errors | Quote validity | Median / p95 latency | Prompt tokens | Prompt tok/s | Generation tok/s | Peak RAM GiB | Peak VRAM MB | 300-control hours |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| M:retrieval | 10 | 60.0% | 0 | 93.8% | 218.270 / 403.891 s | 3459 | 21.8 | 5.4 | 19.09 | n/a | 20.61 |

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
| Mean / median / p95 latency | 247.305 / 218.270 / 403.891 s |
| Min / max latency | 179.784 / 521.039 s |
| Mean prompt processing speed | 21.8 tokens/s |
| Mean generation speed | 5.4 tokens/s |
| Prompt-cache cases / uncached prompt-speed samples | 0 / 10 |
| Mean phase shares: load / prompt / generation | 0.0% / 64.0% / 35.9% |
| Total timed run | 2480.137 s |
| Throughput | 0.24 case repetitions/min |
| Projected 300 controls | 20.67 hours |
| Warm-up load time (separate) | 12.990 s |
| Peak RAM used | 19.09 GiB |
| Ollama server peak RSS | 0.06 GiB |
| Ollama model-runner peak RSS | 7.12 GiB |
| Mean benchmark process CPU | 0.2% |
| Mean / peak system CPU | 60.1% / 98.3% |
| Peak GPU utilization / VRAM | n/a% / n/a MB |
| Resource note | nvidia-smi not installed; GPU metrics unavailable.; NVIDIA utilization/VRAM samples unavailable. |

## Cases needing review

| Case | Expected | Predicted | Match | Truncation | Case file |
|---|---|---|---|---|---|
| heavy-mock-pwd-01-partial-01-m (rep 1) | partial | non_compliant | no | False | [case](cases/heavy-mock-pwd-01-partial-01-m.md) |
| heavy-mock-mfa-02-compliant-01-m (rep 1) | compliant | non_compliant | no | False | [case](cases/heavy-mock-mfa-02-compliant-01-m.md) |
| heavy-mock-log-04-non-compliant-01-m (rep 1) | non_compliant | invalid_output | no | True | [case](cases/heavy-mock-log-04-non-compliant-01-m.md) |
| heavy-mock-patch-05-compliant-01-m (rep 1) | compliant | partial | no | False | [case](cases/heavy-mock-patch-05-compliant-01-m.md) |

## Environment

- OS: Linux-7.0.0-42-generic-x86_64-with-glibc2.43
- CPU: AMD Ryzen 5 5625U with Radeon Graphics (12 logical cores)
- RAM: 30.16 GiB
- GPU: No NVIDIA GPU detected by nvidia-smi; GPU utilization and VRAM sampling are unavailable.
- Backend version: 0.33.2; model digest: 845dbda0ea48ed749caafd9e6037047aa19acfcfd82e704d7ca97d631a0b697e; quantization: Q4_K_M

Warm-up is excluded from the timed case throughput and its reported load time is shown separately. Ollama token counts and timing fields are native when available; OpenAI-compatible prompt counts may fall back to a character-based estimate if the server omits usage.
