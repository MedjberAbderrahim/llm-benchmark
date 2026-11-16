# Retrieval evaluation: heavy

- Dataset hash: `2d78273da105a8ff59d9e96cf6c1ec8a5959f15898a3f73488088fbf53d5a95d`
- Query versions: `['query_v1']`; hints: `[False]`; minimum files: `4`
- Embedding model: `qwen3-embedding:8b`
- Embedding identity: `{"embedding_preset": "qwen3-embed-8b", "embedding_backend": "ollama", "embedding_model": "qwen3-embedding:8b", "embedding_digest": "64b933495768fbd3b87c20583d379728a07471e0c66733a9df87cd1901b3c44b", "embedding_quantization": "Q4_K_M", "embedding_dimension": 4096, "embedding_raw_dimension": 4096, "embedding_requested_dimension": null, "query_prefix": "Instruct: Given a compliance control or requirement, retrieve the evidence passages (policies, procedures, configuration excerpts) that show whether it is met\nQuery: ", "passage_prefix": "", "ollama_version": "0.40.13"}`
- Index: 5783 chunks; 104640137 bytes; cache hit rate 0.0
- No LLM was called.

| Chunk | Overlap | Retriever | Query | Hints | k | Cases | All required gold in context | Recall@k | MRR | Context tokens | Cache hits |
|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 400 | 60 | dense | query_v1 | False | 5 | 108 | 77.4% | 0.884 | 0.995 | 1695 | 0.0% |

## Breakdown by tier, language, control, and tag

### tier

| Value | Cases | All required in context | Recall@k | MRR |
|---|---:|---:|---:|---:|
| L | 38 | 74.2% | 0.873 | 0.984 |
| M | 38 | 90.3% | 0.952 | 1.000 |
| XL | 32 | 67.7% | 0.825 | 1.000 |
### language

| Value | Cases | All required in context | Recall@k | MRR |
|---|---:|---:|---:|---:|
| en | 71 | 75.8% | 0.874 | 0.992 |
| fr | 25 | 83.3% | 0.917 | 1.000 |
| mixed | 12 | 77.8% | 0.889 | 1.000 |
### control_id

| Value | Cases | All required in context | Recall@k | MRR |
|---|---:|---:|---:|---:|
| MOCK-ACCESS-08 | 14 | 33.3% | 0.667 | 1.000 |
| MOCK-FW-06 | 12 | 100.0% | 1.000 | 1.000 |
| MOCK-LOCK-03 | 9 | 88.9% | 0.944 | 1.000 |
| MOCK-LOG-04 | 17 | 73.3% | 0.871 | 1.000 |
| MOCK-MFA-02 | 15 | 58.3% | 0.792 | 0.958 |
| MOCK-PATCH-05 | 13 | 72.7% | 0.826 | 1.000 |
| MOCK-PWD-01 | 15 | 100.0% | 1.000 | 1.000 |
| MOCK-TLS-07 | 13 | 100.0% | 1.000 | 1.000 |
### tags

| Tag | Cases | All required in context | Recall@k | MRR |
|---|---:|---:|---:|---:|
| adv_buried_effective_line | 3 | 66.7% | 0.833 | 0.833 |
| adv_buried_prompt_injection | 3 | 33.3% | 0.667 | 1.000 |
| adv_draft_approved | 3 | 66.7% | 0.833 | 1.000 |
| adv_near_duplicate_number | 3 | 33.3% | 0.667 | 1.000 |
| adv_related_insufficient | 3 | n/a% | n/a | n/a |
| adv_single_csv_exception | 3 | 66.7% | 0.833 | 1.000 |
| adv_superseded | 3 | 66.7% | 0.833 | 1.000 |
| adv_time_limited_exception | 3 | 33.3% | 0.667 | 1.000 |
| adversarial | 24 | 52.4% | 0.756 | 0.976 |
| contradiction | 6 | 83.3% | 0.917 | 0.917 |
| distractor | 6 | 50.0% | 0.750 | 1.000 |
| heavy | 108 | 77.4% | 0.884 | 0.995 |
| injection | 9 | 55.6% | 0.778 | 1.000 |
| insufficient_evidence | 15 | n/a% | n/a | n/a |
| numeric_trap | 12 | 83.3% | 0.917 | 1.000 |
| tier_L | 38 | 74.2% | 0.873 | 0.984 |
| tier_M | 38 | 90.3% | 0.952 | 1.000 |
| tier_XL | 32 | 67.7% | 0.825 | 1.000 |
