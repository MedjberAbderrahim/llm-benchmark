# Retrieval evaluation: base

- Dataset hash: `a1d5f5446bba2ffbf4899027b87c24ef35d8c743f866900ea3dfe934d583a7b8`
- Query template: `query_v1`
- Embedding model: `lexical-only`
- No LLM was called.

| Chunk | Overlap | Retriever | k | Gold passages | Hits | Recall@k | MRR | Mean context tokens | Cache hit rate |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 400 | 60 | bm25 | 5 | 0 | 0 | n/a | n/a | 199 | 0.0% |

## Breakdown by tier, language, control, and tag (chunk 400, bm25)

### tier

| Value | Cases | Recall | MRR | Mean context tokens |
|---|---:|---:|---:|---:|
| S | 3 | 0.000 | 0.000 | 199 |

### language

| Value | Cases | Recall | MRR | Mean context tokens |
|---|---:|---:|---:|---:|
| en | 2 | 0.000 | 0.000 | 210 |
| fr | 1 | 0.000 | 0.000 | 177 |

### control_id

| Value | Cases | Recall | MRR | Mean context tokens |
|---|---:|---:|---:|---:|
| MOCK-PWD-01 | 3 | 0.000 | 0.000 | 199 |

### tags

| Tag | Cases | Recall | MRR |
|---|---:|---:|---:|
| contradiction | 1 | 0.000 | 0.000 |
