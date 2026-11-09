# Benchmark run: 20261108T140221Z_qwen2.5-14b

- Backend/model: `ollama` / `qwen2.5:14b`
- Split: `dev`; cases: 3; repeats: 1
- Prompt: `eval_v1`; output language: `fr`
- Dataset SHA-256: `a1d5f5446bba2ffbf4899027b87c24ef35d8c743f866900ea3dfe934d583a7b8`

## Accuracy and output quality

| Metric | Result |
|---|---:|
| Verdict accuracy (invalid outputs count as wrong) | 66.7% |
| Dangerous false reassurance | 0 |
| Over-strict errors | 1 |
| Valid JSON + schema before repair | 100.0% |
| Valid JSON + schema after repair | 100.0% |
| Schema failures before repair | 0 |
| Repair calls | 0 |
| Quote validity | 100.0% (7/7) |
| Prompt-injection resistance | 100.0% (1 cases) |
| Mean confidence, correct / incorrect | 1.000 / 1.000 |

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

## Performance

| Metric | Result |
|---|---:|
| Mean / median / p95 latency | 223.017 / 219.500 / 233.708 s |
| Min / max latency | 214.265 / 235.287 s |
| Mean prompt processing speed | 13.7 tokens/s |
| Mean generation speed | 3.1 tokens/s |
| Total timed run | 669.069 s |
| Throughput | 0.27 case repetitions/min |
| Projected 300 controls | 18.59 hours |
| Warm-up load time (separate) | 29.129 s |
| Peak RAM used | 28.08 GiB |
| Ollama server peak RSS | 0.06 GiB |
| Ollama model-runner peak RSS | 10.77 GiB |
| Mean benchmark process CPU | 0.2% |
| Mean / peak system CPU | 60.3% / 95.2% |
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
- Backend version: 0.33.2; model digest: 7cdf5a0187d5c58cc5d369b255592f7841d1c4696d45a8c8a9489440385b22f6; quantization: Q4_K_M

Warm-up is excluded from the timed case throughput and its reported load time is shown separately. Ollama token counts and timing fields are native when available; OpenAI-compatible prompt counts may fall back to a character-based estimate if the server omits usage.
