# Retrieval evaluation: heavy

- Dataset hash: `2d78273da105a8ff59d9e96cf6c1ec8a5959f15898a3f73488088fbf53d5a95d`
- Query versions: `['query_v1']`; hints: `[False]`; minimum files: `4`
- Embedding model: `bge-m3`
- Embedding identity: `{"embedding_preset": "bge-m3", "embedding_backend": "ollama", "embedding_model": "bge-m3", "embedding_digest": "7907646426070047a77226ac3e684fbbe8410524f7b4a74d02837e43f2146bab", "embedding_quantization": "F16", "embedding_dimension": 1024, "embedding_raw_dimension": 1024, "embedding_requested_dimension": null, "query_prefix": "", "passage_prefix": "", "ollama_version": "0.40.13"}`
- Index: 5783 chunks; 33578633 bytes; cache hit rate 0.0
- No LLM was called.

| Chunk | Overlap | Retriever | Query | Hints | k | Cases | All required gold in context | Recall@k | MRR | Context tokens | Cache hits |
|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 400 | 60 | dense | query_v1 | False | 5 | 108 | 76.3% | 0.884 | 0.995 | 1597 | 0.0% |

## Breakdown by tier, language, control, and tag

### tier

| Value | Cases | All required in context | Recall@k | MRR |
|---|---:|---:|---:|---:|
| L | 38 | 67.7% | 0.841 | 0.984 |
| M | 38 | 93.5% | 0.968 | 1.000 |
| XL | 32 | 67.7% | 0.841 | 1.000 |
### language

| Value | Cases | All required in context | Recall@k | MRR |
|---|---:|---:|---:|---:|
| en | 71 | 72.7% | 0.867 | 0.992 |
| fr | 25 | 77.8% | 0.889 | 1.000 |
| mixed | 12 | 100.0% | 1.000 | 1.000 |
### control_id

| Value | Cases | All required in context | Recall@k | MRR |
|---|---:|---:|---:|---:|
| MOCK-ACCESS-08 | 14 | 41.7% | 0.708 | 1.000 |
| MOCK-FW-06 | 12 | 90.9% | 0.955 | 1.000 |
| MOCK-LOCK-03 | 9 | 77.8% | 0.889 | 1.000 |
| MOCK-LOG-04 | 17 | 86.7% | 0.935 | 1.000 |
| MOCK-MFA-02 | 15 | 83.3% | 0.917 | 1.000 |
| MOCK-PATCH-05 | 13 | 72.7% | 0.870 | 1.000 |
| MOCK-PWD-01 | 15 | 76.9% | 0.889 | 1.000 |
| MOCK-TLS-07 | 13 | 80.0% | 0.900 | 0.950 |
### tags

| Tag | Cases | All required in context | Recall@k | MRR |
|---|---:|---:|---:|---:|
| adv_buried_effective_line | 3 | 33.3% | 0.667 | 1.000 |
| adv_buried_prompt_injection | 3 | 100.0% | 1.000 | 1.000 |
| adv_draft_approved | 3 | 66.7% | 0.833 | 1.000 |
| adv_near_duplicate_number | 3 | 100.0% | 1.000 | 1.000 |
| adv_related_insufficient | 3 | n/a% | n/a | n/a |
| adv_single_csv_exception | 3 | 33.3% | 0.667 | 1.000 |
| adv_superseded | 3 | 100.0% | 1.000 | 0.833 |
| adv_time_limited_exception | 3 | 100.0% | 1.000 | 1.000 |
| adversarial | 24 | 76.2% | 0.889 | 0.976 |
| contradiction | 6 | 66.7% | 0.833 | 1.000 |
| distractor | 6 | 50.0% | 0.750 | 1.000 |
| heavy | 108 | 76.3% | 0.884 | 0.995 |
| injection | 9 | 88.9% | 0.944 | 1.000 |
| insufficient_evidence | 15 | n/a% | n/a | n/a |
| numeric_trap | 12 | 91.7% | 0.958 | 1.000 |
| tier_L | 38 | 67.7% | 0.841 | 0.984 |
| tier_M | 38 | 93.5% | 0.968 | 1.000 |
| tier_XL | 32 | 67.7% | 0.841 | 1.000 |
