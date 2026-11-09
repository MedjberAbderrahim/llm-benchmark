# Benchmark run: 20261108T173918Z_qwen2.5-7b_heavy_retrieval_M

- Backend/model: `ollama` / `qwen2.5:7b`
- Split: `dev`; cases: 1; repeats: 1
- Completion: complete
- Prompt: `eval_v2_retrieval`; query template: `query_v1`; output language: `fr`
- Dataset SHA-256: `141ed4ece6a13cf0bb8fbd2bedadc1cb3854df935f2480af75e5186102dba3cd`

## Accuracy and output quality

| Metric | Result |
|---|---:|
| Verdict accuracy (invalid outputs count as wrong) | 0.0% |
| Dangerous false reassurance | 0 |
| Over-strict errors | 0 |
| Valid JSON before repair | 100.0% |
| Valid JSON after repair | 100.0% |
| Schema-valid before / after repair | 100.0% / 100.0% |
| Schema failures before repair | 0 |
| Repair calls | 0 |
| Quote validity | 100.0% (1/1) |
| Prompt-injection resistance | n/a% (0 cases) |
| Mean confidence, correct / incorrect | n/a / 0.700 |

### Confusion matrix

| Expected \ Predicted | compliant | partial | non_compliant | insufficient_evidence |
|---|---:|---:|---:|---:|
| compliant | 0 | 0 | 0 | 0 |
| partial | 0 | 0 | 0 | 1 |
| non_compliant | 0 | 0 | 0 | 0 |
| insufficient_evidence | 0 | 0 | 0 | 0 |

### Per-class precision and recall

| Status | Precision | Recall | Support |
|---|---:|---:|---:|
| compliant | n/a | n/a | 0 |
| partial | n/a | 0.00 | 1 |
| non_compliant | n/a | n/a | 0 |
| insufficient_evidence | 0.00 | n/a | 0 |

### Accuracy by language

| Language | Cases | Accuracy |
|---|---:|---:|
| en | 0 | n/a% |
| fr | 1 | 0.0% |
| mixed | 0 | n/a% |

### Accuracy by tag

| Tag | Cases | Accuracy |
|---|---:|---:|
| contradiction | 1 | 0.0% |
| heavy | 1 | 0.0% |
| tier_M | 1 | 0.0% |

### Confidence calibration

| Confidence bucket | Cases | Mean confidence | Accuracy |
|---|---:|---:|---:|
| 0.0-0.2 | 0 | n/a | n/a% |
| 0.2-0.4 | 0 | n/a | n/a% |
| 0.4-0.6 | 0 | n/a | n/a% |
| 0.6-0.8 | 1 | 0.70 | 0.0% |
| 0.8-1.0 | 0 | n/a | n/a% |

### Needle position accuracy (full context)

| Position | Cases | Accuracy |
|---|---:|---:|
| end | 0 | n/a% |
| middle | 0 | n/a% |
| start | 0 | n/a% |

### Scaling by tier and context mode

| Tier / mode | Cases | Accuracy | Dangerous errors | Quote validity | Median / p95 latency | Prompt tokens | Prompt tok/s | Generation tok/s | Peak RAM GiB | Peak VRAM MB | 300-control hours |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| M:retrieval | 1 | 0.0% | 0 | 100.0% | 151.787 / 151.787 s | 2611 | 27.6 | 6.6 | 16.78 | n/a | 12.65 |

### Paired heavy variants

| Base case | Available tiers | Verdict changes vs S | Latency growth ratios vs S |
|---|---|---:|---|
| mock-pwd-01-partial-01 | M | None | compare with a base S run |

## Performance

| Metric | Result |
|---|---:|
| Mean / median / p95 latency | 151.787 / 151.787 / 151.787 s |
| Min / max latency | 151.787 / 151.787 s |
| Mean prompt processing speed | 27.6 tokens/s |
| Mean generation speed | 6.6 tokens/s |
| Prompt-cache cases / uncached prompt-speed samples | 0 / 1 |
| Mean phase shares: load / prompt / generation | 0.0% / 62.3% / 37.7% |
| Total timed run | 151.862 s |
| Throughput | 0.40 case repetitions/min |
| Projected 300 controls | 12.66 hours |
| Warm-up load time (separate) | 0.002 s |
| Peak RAM used | 16.78 GiB |
| Ollama server peak RSS | 0.05 GiB |
| Ollama model-runner peak RSS | 5.12 GiB |
| Mean benchmark process CPU | 0.2% |
| Mean / peak system CPU | 52.1% / 75.1% |
| Peak GPU utilization / VRAM | n/a% / n/a MB |
| Resource note | nvidia-smi not installed; GPU metrics unavailable.; NVIDIA utilization/VRAM samples unavailable. |

## Cases needing review

| Case | Expected | Predicted | Match | Truncation | Case file |
|---|---|---|---|---|---|
| heavy-mock-pwd-01-partial-01-m (rep 1) | partial | insufficient_evidence | no | False | [case](cases/heavy-mock-pwd-01-partial-01-m.md) |

## Environment

- OS: Linux-7.0.0-42-generic-x86_64-with-glibc2.43
- CPU: AMD Ryzen 5 5625U with Radeon Graphics (12 logical cores)
- RAM: 30.16 GiB
- GPU: No NVIDIA GPU detected by nvidia-smi; GPU utilization and VRAM sampling are unavailable.
- Backend version: 0.33.2; model digest: 845dbda0ea48ed749caafd9e6037047aa19acfcfd82e704d7ca97d631a0b697e; quantization: Q4_K_M

Warm-up is excluded from the timed case throughput and its reported load time is shown separately. Ollama token counts and timing fields are native when available; OpenAI-compatible prompt counts may fall back to a character-based estimate if the server omits usage.
