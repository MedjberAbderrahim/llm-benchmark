# Retrieval evaluation: heavy

- Dataset hash: `2d78273da105a8ff59d9e96cf6c1ec8a5959f15898a3f73488088fbf53d5a95d`
- Query versions: `['query_v1']`; hints: `[False]`; minimum files: `4`
- Embedding model: `maternion/nemotron-3.5-embed:8b-q4_k_m`
- Embedding identity: `{"embedding_preset": "nemotron-embed-8b", "embedding_backend": "ollama", "embedding_model": "maternion/nemotron-3.5-embed:8b-q4_k_m", "embedding_digest": "63bc01b981da0e235c5000ff58c8ea807d270ce57cb3aa4a536123b932cae5b2", "embedding_quantization": "Q4_K_M", "embedding_dimension": 4096, "embedding_raw_dimension": 4096, "embedding_requested_dimension": null, "query_prefix": "query: ", "passage_prefix": "passage: ", "ollama_version": "0.40.13"}`
- Index: 5783 chunks; 104640137 bytes; cache hit rate 0.0
- No LLM was called.

| Chunk | Overlap | Retriever | Query | Hints | k | Cases | All required gold in context | Recall@k | MRR | Context tokens | Cache hits |
|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 400 | 60 | dense | query_v1 | False | 5 | 108 | 91.4% | 0.958 | 1.000 | 1624 | 0.0% |

## Breakdown by tier, language, control, and tag

### tier

| Value | Cases | All required in context | Recall@k | MRR |
|---|---:|---:|---:|---:|
| L | 38 | 90.3% | 0.952 | 1.000 |
| M | 38 | 93.5% | 0.968 | 1.000 |
| XL | 32 | 90.3% | 0.952 | 1.000 |
### language

| Value | Cases | All required in context | Recall@k | MRR |
|---|---:|---:|---:|---:|
| en | 71 | 92.4% | 0.963 | 1.000 |
| fr | 25 | 83.3% | 0.917 | 1.000 |
| mixed | 12 | 100.0% | 1.000 | 1.000 |
### control_id

| Value | Cases | All required in context | Recall@k | MRR |
|---|---:|---:|---:|---:|
| MOCK-ACCESS-08 | 14 | 50.0% | 0.750 | 1.000 |
| MOCK-FW-06 | 12 | 100.0% | 1.000 | 1.000 |
| MOCK-LOCK-03 | 9 | 88.9% | 0.944 | 1.000 |
| MOCK-LOG-04 | 17 | 100.0% | 1.000 | 1.000 |
| MOCK-MFA-02 | 15 | 100.0% | 1.000 | 1.000 |
| MOCK-PATCH-05 | 13 | 90.9% | 0.957 | 1.000 |
| MOCK-PWD-01 | 15 | 100.0% | 1.000 | 1.000 |
| MOCK-TLS-07 | 13 | 100.0% | 1.000 | 1.000 |
### tags

| Tag | Cases | All required in context | Recall@k | MRR |
|---|---:|---:|---:|---:|
| adv_buried_effective_line | 3 | 100.0% | 1.000 | 1.000 |
| adv_buried_prompt_injection | 3 | 100.0% | 1.000 | 1.000 |
| adv_draft_approved | 3 | 100.0% | 1.000 | 1.000 |
| adv_near_duplicate_number | 3 | 100.0% | 1.000 | 1.000 |
| adv_related_insufficient | 3 | n/a% | n/a | n/a |
| adv_single_csv_exception | 3 | 66.7% | 0.833 | 1.000 |
| adv_superseded | 3 | 100.0% | 1.000 | 1.000 |
| adv_time_limited_exception | 3 | 100.0% | 1.000 | 1.000 |
| adversarial | 24 | 95.2% | 0.978 | 1.000 |
| contradiction | 6 | 100.0% | 1.000 | 1.000 |
| distractor | 6 | 50.0% | 0.750 | 1.000 |
| heavy | 108 | 91.4% | 0.958 | 1.000 |
| injection | 9 | 100.0% | 1.000 | 1.000 |
| insufficient_evidence | 15 | n/a% | n/a | n/a |
| numeric_trap | 12 | 100.0% | 1.000 | 1.000 |
| tier_L | 38 | 90.3% | 0.952 | 1.000 |
| tier_M | 38 | 93.5% | 0.968 | 1.000 |
| tier_XL | 32 | 90.3% | 0.952 | 1.000 |
