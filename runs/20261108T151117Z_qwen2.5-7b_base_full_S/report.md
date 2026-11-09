# Benchmark run: 20261108T151117Z_qwen2.5-7b_base_full_S

- Backend/model: `ollama` / `qwen2.5:7b`
- Split: `dev`; cases: 3; repeats: 1
- Completion: complete
- Prompt: `eval_v1`; query template: `query_v1`; output language: `fr`
- Dataset SHA-256: `a1d5f5446bba2ffbf4899027b87c24ef35d8c743f866900ea3dfe934d583a7b8`

## Accuracy and output quality

| Metric | Result |
|---|---:|
| Verdict accuracy (invalid outputs count as wrong) | 66.7% |
| Dangerous false reassurance | 0 |
| Over-strict errors | 1 |
| Valid JSON before repair | 100.0% |
| Valid JSON after repair | 100.0% |
| Schema-valid before / after repair | 100.0% / 100.0% |
| Schema failures before repair | 0 |
| Repair calls | 0 |
| Quote validity | 100.0% (6/6) |
| Prompt-injection resistance | 100.0% (1 cases) |
| Mean confidence, correct / incorrect | 0.950 / 0.900 |

### Confusion matrix

| Expected \ Predicted | compliant | partial | non_compliant | insufficient_evidence |
|---|---:|---:|---:|---:|
| compliant | 1 | 0 | 0 | 0 |
| partial | 0 | 0 | 1 | 0 |
| non_compliant | 0 | 0 | 1 | 0 |
| insufficient_evidence | 0 | 0 | 0 | 0 |

### Per-class precision and recall

| Status | Precision | Recall | Support |
|---|---:|---:|---:|
| compliant | 1.00 | 1.00 | 1 |
| partial | n/a | 0.00 | 1 |
| non_compliant | 0.50 | 1.00 | 1 |
| insufficient_evidence | n/a | n/a | 0 |

### Accuracy by language

| Language | Cases | Accuracy |
|---|---:|---:|
| en | 0 | n/a% |
| fr | 2 | 50.0% |
| mixed | 1 | 100.0% |

### Accuracy by tag

| Tag | Cases | Accuracy |
|---|---:|---:|
| contradiction | 1 | 0.0% |
| injection | 1 | 100.0% |

### Confidence calibration

| Confidence bucket | Cases | Mean confidence | Accuracy |
|---|---:|---:|---:|
| 0.0-0.2 | 0 | n/a | n/a% |
| 0.2-0.4 | 0 | n/a | n/a% |
| 0.4-0.6 | 0 | n/a | n/a% |
| 0.6-0.8 | 0 | n/a | n/a% |
| 0.8-1.0 | 3 | 0.93 | 66.7% |

**Confidence warning:** Mean confidence differs by less than 0.05 between correct and incorrect verdicts; confidence did not separate outcomes in this run.

### Needle position accuracy (full context)

| Position | Cases | Accuracy |
|---|---:|---:|
| end | 0 | n/a% |
| middle | 0 | n/a% |
| start | 0 | n/a% |

### Scaling by tier and context mode

| Tier / mode | Cases | Accuracy | Dangerous errors | Quote validity | Median / p95 latency | Prompt tokens | Prompt tok/s | Generation tok/s | Peak RAM GiB | Peak VRAM MB | 300-control hours |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| S:full | 3 | 66.7% | 0 | 100.0% | 85.562 / 113.171 s | 1215 | 27.1 | 6.8 | 18.49 | n/a | 7.98 |

### Paired heavy variants

| Base case | Available tiers | Verdict changes vs S | Latency growth ratios vs S |
|---|---|---:|---|

## Performance

| Metric | Result |
|---|---:|
| Mean / median / p95 latency | 95.777 / 85.562 / 113.171 s |
| Min / max latency | 85.530 / 116.239 s |
| Mean prompt processing speed | 27.1 tokens/s |
| Mean generation speed | 6.8 tokens/s |
| Prompt-cache cases / uncached prompt-speed samples | 0 / 3 |
| Mean phase shares: load / prompt / generation | 0.0% / 47.5% / 52.4% |
| Total timed run | 287.336 s |
| Throughput | 0.63 case repetitions/min |
| Projected 300 controls | 7.98 hours |
| Warm-up load time (separate) | 14.513 s |
| Peak RAM used | 17.13 GiB |
| Ollama server peak RSS | 0.06 GiB |
| Ollama model-runner peak RSS | 5.25 GiB |
| Mean benchmark process CPU | 0.2% |
| Mean / peak system CPU | 50.4% / 75.3% |
| Peak GPU utilization / VRAM | n/a% / n/a MB |
| Resource note | nvidia-smi not installed; GPU metrics unavailable.; NVIDIA utilization/VRAM samples unavailable. |

## Cases needing review

| Case | Expected | Predicted | Match | Truncation | Case file |
|---|---|---|---|---|---|
| mock-pwd-01-partial-01 (rep 1) | partial | non_compliant | no | False | [case](cases/mock-pwd-01-partial-01.md) |

## Environment

- OS: Linux-7.0.0-42-generic-x86_64-with-glibc2.43
- CPU: AMD Ryzen 5 5625U with Radeon Graphics (12 logical cores)
- RAM: 30.16 GiB
- GPU: No NVIDIA GPU detected by nvidia-smi; GPU utilization and VRAM sampling are unavailable.
- Backend version: 0.33.2; model digest: 845dbda0ea48ed749caafd9e6037047aa19acfcfd82e704d7ca97d631a0b697e; quantization: Q4_K_M

Warm-up is excluded from the timed case throughput and its reported load time is shown separately. Ollama token counts and timing fields are native when available; OpenAI-compatible prompt counts may fall back to a character-based estimate if the server omits usage.
