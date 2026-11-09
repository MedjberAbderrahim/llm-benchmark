# Benchmark comparison

## Warnings

- **Warning:** Runs use different dataset hashes; accuracy and performance are not directly comparable.
- **Warning:** Runs use different evaluation prompt versions; accuracy may not be directly comparable.

| Run / model | Dataset | Context | Tier(s) | Accuracy | Dangerous errors | Quote validity | JSON valid after retry | Median latency | P95 latency | Prompt tok/s | Generation tok/s | Peak RAM GiB | Peak VRAM MB | 300-control hours |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 20261108T151117Z_qwen2.5-7b_base_full_S / `qwen2.5:7b` | base | full | S | 66.7% | 0 | 100.0% | 100.0% | 85.562 s | 113.171 s | 27.1 | 6.8 | 17.13 | n/a | 7.98 |
| 20261108T173918Z_qwen2.5-7b_heavy_retrieval_M / `qwen2.5:7b` | heavy | retrieval | M | 0.0% | 0 | 100.0% | 100.0% | 151.787 s | 151.787 s | 27.6 | 6.6 | 16.78 | n/a | 12.66 |

## Scaling by tier and context mode

| Run / model | Tier / mode | Cases | Accuracy | Dangerous errors | Quote validity | Median / p95 latency | Prompt tokens | Prompt tok/s | Generation tok/s | Peak RAM GiB | Peak VRAM MB | 300-control hours |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 20261108T151117Z_qwen2.5-7b_base_full_S / `qwen2.5:7b` | S:full | 3 | 66.7% | 0 | 100.0% | 85.562 / 113.171 s | 1215 | 27.1 | 6.8 | 18.49 | n/a | 7.98 |
| 20261108T173918Z_qwen2.5-7b_heavy_retrieval_M / `qwen2.5:7b` | M:retrieval | 1 | 0.0% | 0 | 100.0% | 151.787 / 151.787 s | 2611 | 27.6 | 6.6 | 16.78 | n/a | 12.65 |

## Paired verdict and latency comparison

| Base case / model / mode | Tiers observed | Verdict changes vs S | Median latency growth vs S by tier |
|---|---|---:|---|
| mock-mfa-02-compliant-01 / `qwen2.5:7b` / full | S | 0 | n/a |
| mock-mfa-02-non-compliant-01 / `qwen2.5:7b` / full | S | 0 | n/a |
| mock-pwd-01-partial-01 / `qwen2.5:7b` / full | S | 0 | n/a |
| mock-pwd-01-partial-01 / `qwen2.5:7b` / retrieval | M | base S run not included | base S run not included |
