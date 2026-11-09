# Benchmark comparison

| Run / model | Accuracy | Dangerous errors | Quote validity | JSON valid after retry | Median latency | P95 latency | Prompt tok/s | Generation tok/s | Peak RAM GiB | Peak VRAM MB | 300-control hours |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 20261108T135629Z_qwen2.5-7b / `qwen2.5:7b` | 66.7% | 0 | 100.0% | 100.0% | 43.497 s | 51.445 s | 8072.3 | 6.9 | 18.20 | n/a | 3.83 |
| 20261108T140221Z_qwen2.5-14b / `qwen2.5:14b` | 66.7% | 0 | 100.0% | 100.0% | 219.500 s | 233.708 s | 13.7 | 3.1 | 28.08 | n/a | 18.59 |
