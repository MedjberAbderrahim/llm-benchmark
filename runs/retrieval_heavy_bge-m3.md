# Retrieval evaluation: heavy

- Dataset hash: `5a76ddb31b5b2b25fff6101cd161227efb7870eee16f765348c7d8d8828c12ea`
- Query versions: `['query_v1', 'query_v2']`; hints: `[False, True]`; minimum files: `4`
- Embedding model: `bge-m3`
- No LLM was called.

| Chunk | Overlap | Retriever | Query | Hints | k | Cases | All required gold in context | Recall@k | MRR | Context tokens | Cache hits |
|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 400 | 60 | dense | query_v1 | False | 5 | 12 | 83.3% | 0.917 | 1.000 | 1710 | 0.0% |
| 400 | 60 | dense | query_v1 | False | 8 | 12 | 83.3% | 0.917 | 1.000 | 2859 | 0.0% |
| 400 | 60 | dense | query_v1 | True | 5 | 12 | 91.7% | 0.958 | 1.000 | 1715 | 0.0% |
| 400 | 60 | dense | query_v1 | True | 8 | 12 | 91.7% | 0.958 | 1.000 | 2857 | 0.0% |
| 400 | 60 | dense | query_v2 | False | 5 | 12 | 91.7% | 0.958 | 1.000 | 1683 | 0.0% |
| 400 | 60 | dense | query_v2 | False | 8 | 12 | 91.7% | 0.958 | 1.000 | 2773 | 0.0% |
| 400 | 60 | dense | query_v2 | True | 5 | 12 | 91.7% | 0.958 | 1.000 | 1688 | 0.0% |
| 400 | 60 | dense | query_v2 | True | 8 | 12 | 91.7% | 0.958 | 1.000 | 2824 | 0.0% |
| 400 | 60 | bm25 | query_v1 | False | 5 | 12 | 8.3% | 0.542 | 1.000 | 1871 | 0.0% |
| 400 | 60 | bm25 | query_v1 | False | 8 | 12 | 8.3% | 0.542 | 1.000 | 2969 | 0.0% |
| 400 | 60 | bm25 | query_v1 | True | 5 | 12 | 66.7% | 0.833 | 1.000 | 1811 | 0.0% |
| 400 | 60 | bm25 | query_v1 | True | 8 | 12 | 66.7% | 0.833 | 1.000 | 2911 | 0.0% |
| 400 | 60 | bm25 | query_v2 | False | 5 | 12 | 0.0% | 0.500 | 1.000 | 1904 | 0.0% |
| 400 | 60 | bm25 | query_v2 | False | 8 | 12 | 0.0% | 0.500 | 1.000 | 3000 | 0.0% |
| 400 | 60 | bm25 | query_v2 | True | 5 | 12 | 100.0% | 1.000 | 1.000 | 1821 | 0.0% |
| 400 | 60 | bm25 | query_v2 | True | 8 | 12 | 100.0% | 1.000 | 1.000 | 2873 | 0.0% |
| 400 | 60 | hybrid | query_v1 | False | 5 | 12 | 33.3% | 0.667 | 1.000 | 1864 | 0.0% |
| 400 | 60 | hybrid | query_v1 | False | 8 | 12 | 33.3% | 0.667 | 1.000 | 2990 | 0.0% |
| 400 | 60 | hybrid | query_v1 | True | 5 | 12 | 75.0% | 0.875 | 1.000 | 1795 | 0.0% |
| 400 | 60 | hybrid | query_v1 | True | 8 | 12 | 75.0% | 0.875 | 1.000 | 2924 | 0.0% |
| 400 | 60 | hybrid | query_v2 | False | 5 | 12 | 16.7% | 0.583 | 1.000 | 1821 | 0.0% |
| 400 | 60 | hybrid | query_v2 | False | 8 | 12 | 16.7% | 0.583 | 1.000 | 2952 | 0.0% |
| 400 | 60 | hybrid | query_v2 | True | 5 | 12 | 100.0% | 1.000 | 1.000 | 1784 | 0.0% |
| 400 | 60 | hybrid | query_v2 | True | 8 | 12 | 100.0% | 1.000 | 1.000 | 2868 | 0.0% |

## Breakdown by tier, language, control, and tag

### tier

| Value | Cases | All required in context | Recall@k | MRR |
|---|---:|---:|---:|---:|
| L | 4 | 100.0% | 1.000 | 1.000 |
| M | 4 | 100.0% | 1.000 | 1.000 |
| XL | 4 | 100.0% | 1.000 | 1.000 |
### language

| Value | Cases | All required in context | Recall@k | MRR |
|---|---:|---:|---:|---:|
| en | 6 | 100.0% | 1.000 | 1.000 |
| fr | 6 | 100.0% | 1.000 | 1.000 |
### control_id

| Value | Cases | All required in context | Recall@k | MRR |
|---|---:|---:|---:|---:|
| MOCK-MFA-02 | 6 | 100.0% | 1.000 | 1.000 |
| MOCK-PWD-01 | 6 | 100.0% | 1.000 | 1.000 |
### tags

| Tag | Cases | All required in context | Recall@k | MRR |
|---|---:|---:|---:|---:|
| heavy | 12 | 100.0% | 1.000 | 1.000 |
| tier_L | 4 | 100.0% | 1.000 | 1.000 |
| tier_M | 4 | 100.0% | 1.000 | 1.000 |
| tier_XL | 4 | 100.0% | 1.000 | 1.000 |
