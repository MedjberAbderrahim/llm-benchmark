# Benchmark run: 20261109T134902Z_qwen2.5-14b_heavy_retrieval_M

- Backend/model: `ollama` / `qwen2.5:14b`
- Split: `dev`; cases: 10; repeats: 1
- Completion: complete
- Prompt: `eval_v2_retrieval`; query template: `query_v1`; output language: `fr`
- Dataset SHA-256: `5a76ddb31b5b2b25fff6101cd161227efb7870eee16f765348c7d8d8828c12ea`

## Accuracy and output quality

| Metric                                                               |           Result |
| -------------------------------------------------------------------- | ---------------: |
| Verdict accuracy (invalid outputs count as wrong)                    |            70.0% |
| Firm-label accuracy (8 cases)                                        |            62.5% |
| Ambiguous-label accuracy (2 cases)                                   |           100.0% |
| Lenient ambiguous accuracy (partial / non-compliant interchangeable) |           100.0% |
| Dangerous false reassurance                                          |                0 |
| Over-strict errors                                                   |                2 |
| Valid JSON before repair                                             |            90.0% |
| Valid JSON after repair                                              |            90.0% |
| Schema-valid before / after repair                                   |    90.0% / 90.0% |
| Schema failures before repair                                        |                1 |
| Repair calls                                                         |                0 |
| Quote validity                                                       |   100.0% (18/18) |
| Prompt-injection resistance                                          | 100.0% (1 cases) |
| Mean confidence, correct / incorrect                                 |    0.900 / 0.750 |

### Confusion matrix

| Expected \ Predicted | compliant | partial | non_compliant | insufficient_evidence |
|---|---:|---:|---:|---:|
| compliant | 1 | 2 | 0 | 0 |
| partial | 0 | 3 | 0 | 0 |
| non_compliant | 0 | 0 | 3 | 0 |
| insufficient_evidence | 0 | 0 | 0 | 0 |

### Per-class precision and recall

| Status | Precision | Recall | Support |
|---|---:|---:|---:|
| compliant | 1.00 | 0.25 | 4 |
| partial | 0.60 | 1.00 | 3 |
| non_compliant | 1.00 | 1.00 | 3 |
| insufficient_evidence | n/a | n/a | 0 |

### Accuracy by language

| Language | Cases | Accuracy |
|---|---:|---:|
| en | 5 | 60.0% |
| fr | 2 | 50.0% |
| mixed | 3 | 100.0% |

### Accuracy by tag

| Tag | Cases | Accuracy |
|---|---:|---:|
| contradiction | 1 | 100.0% |
| distractor | 1 | 0.0% |
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
| 0.6-0.8 | 1 | 0.70 | 0.0% |
| 0.8-1.0 | 8 | 0.89 | 87.5% |

### Needle position accuracy (full context)

| Position | Cases | Accuracy |
|---|---:|---:|
| end | 0 | n/a% |
| middle | 0 | n/a% |
| start | 0 | n/a% |

### Scaling by tier and context mode

| Tier / mode | Cases | Accuracy | Dangerous errors | Quote validity | Median / p95 latency | Prompt tokens | Prompt tok/s | Generation tok/s | Peak RAM GiB | Peak VRAM MB | 300-control hours |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| M:retrieval | 10 | 70.0% | 0 | 100.0% | 503.690 / 766.853 s | 2687 | 9.4 | 2.6 | 27.80 | n/a | 45.05 |

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

| Metric                                             |                                                                                           Result |
| -------------------------------------------------- | -----------------------------------------------------------------------------------------------: |
| Mean / median / p95 latency                        |                                                                    540.582 / 503.690 / 766.853 s |
| Min / max latency                                  |                                                                              413.758 / 900.103 s |
| Mean prompt processing speed                       |                                                                                     9.4 tokens/s |
| Mean generation speed                              |                                                                                     2.6 tokens/s |
| Prompt-cache cases / uncached prompt-speed samples |                                                                                            0 / 9 |
| Mean phase shares: load / prompt / generation      |                                                                             0.0% / 63.7% / 35.0% |
| Total timed run                                    |                                                                                       5442.316 s |
| Throughput                                         |                                                                        0.11 case repetitions/min |
| Projected 300 controls                             |                                                                                      45.35 hours |
| Warm-up load time (separate)                       |                                                                                         25.030 s |
| Peak RAM used                                      |                                                                                        27.80 GiB |
| Ollama server peak RSS                             |                                                                                         0.06 GiB |
| Ollama model-runner peak RSS                       |                                                                                        16.05 GiB |
| Mean benchmark process CPU                         |                                                                                             0.2% |
| Mean / peak system CPU                             |                                                                                    58.1% / 92.4% |
| Peak GPU utilization / VRAM                        |                                                                                    n/a% / n/a MB |
| Resource note                                      | nvidia-smi not installed; GPU metrics unavailable.; NVIDIA utilization/VRAM samples unavailable. |

## Cases needing review

| Case | Expected | Predicted | Match | Truncation | Case file |
|---|---|---|---|---|---|
| heavy-mock-mfa-02-compliant-01-m (rep 1) | compliant | timeout | no | False | [case](cases/heavy-mock-mfa-02-compliant-01-m.md) |
| heavy-mock-patch-05-compliant-01-m (rep 1) | compliant | partial | no | False | [case](cases/heavy-mock-patch-05-compliant-01-m.md) |
| heavy-mock-fw-06-compliant-01-m (rep 1) | compliant | partial | no | False | [case](cases/heavy-mock-fw-06-compliant-01-m.md) |

## Environment

- OS: Linux-7.0.0-42-generic-x86_64-with-glibc2.43
- CPU: AMD Ryzen 5 5625U with Radeon Graphics (12 logical cores)
- RAM: 30.16 GiB
- GPU: No NVIDIA GPU detected by nvidia-smi; GPU utilization and VRAM sampling are unavailable.
- Backend version: 0.33.2; model digest: 7cdf5a0187d5c58cc5d369b255592f7841d1c4696d45a8c8a9489440385b22f6; quantization: Q4_K_M

Warm-up is excluded from the timed case throughput and its reported load time is shown separately. Ollama token counts and timing fields are native when available; OpenAI-compatible prompt counts may fall back to a character-based estimate if the server omits usage.
