# Local control evaluation benchmark

A small Python benchmark for a **local or self-hosted LLM that assists a human auditor** with mock security-control assessments. The model reads one control and mock evidence, returns a structured verdict and exact quotes, and never makes the final audit decision. Full-context evaluation remains available; a separate retrieval mode can select evidence excerpts. There is no chatbot, OCR, cloud inference, Excel integration, or real client data.

All controls and organizations in `data/` are fictional. Controls are paraphrased themes inspired by PCI DSS v4.0.1, labeled **mock, not authoritative**, and are not a substitute for the standard or an audit interpretation.

## Setup

Python 3.10 or later is required. In this workspace the interpreter is available as `python3`.

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements-dev.txt
python3 -m bench generate-data
python3 -m bench validate-data
python3 -m pytest -q
```

`generate-data` creates the controls, evidence, and labels only when absent. Use `--force` to regenerate all generated mock data. Generation is deterministic. `validate-data` checks control structure, label statuses and splits, case uniqueness, and every evidence reference.

### Windows setup (PowerShell)

Install Python 3.10 or later and Git for Windows. From the repository directory, create and activate a virtual environment and install the project dependencies:

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
python -m bench validate-data --dataset base
python -m pytest -q
```

If PowerShell blocks activation, use `\.venv\Scripts\python.exe` in place of `python` for each command. The Makefile targets and `source .venv/bin/activate` examples below are for Unix-like shells; they are not required on Windows.

The generated heavy evidence is included in this repository, so it does not need to be regenerated after cloning. Validate it with `python -m bench validate-data --dataset heavy`. To regenerate it intentionally, use `python -m bench generate-heavy-data`.

Install Ollama for Windows and start its service/application, then pull a model in PowerShell:

```powershell
ollama pull qwen2.5:7b
python -m bench run --backend ollama --model qwen2.5:7b --dataset base --split dev --limit 5
```

The checked-in `.env.example` contains placeholders only. Copy it to `.env` for local settings; `.env` is ignored by Git. The benchmark does not automatically load dotenv files, so set the needed environment variable in the shell or pass the key explicitly. For example, in PowerShell:

```powershell
Copy-Item .env.example .env
$env:LOCAL_LLM_API_KEY = "replace-with-your-private-key"
python -m bench run --backend openai --base-url http://localhost:8000/v1 --model Qwen/Qwen2.5-14B-Instruct --api-key $env:LOCAL_LLM_API_KEY --limit 5
```

For a local Ollama run, no API key is needed. Never replace placeholders in `.env.example` with real credentials; put private values only in ignored `.env` or in the process environment.

## Laptop run with Ollama

Install and start Ollama, then fetch each model before running it:

```bash
ollama serve
ollama pull qwen2.5:7b
python3 -m bench run --backend ollama --model qwen2.5:7b --split dev --num-ctx 8192 --repeat 1 --limit 5
```

To compare the 14B model on the same cases and settings:

```bash
ollama pull qwen2.5:14b
python3 -m bench run --backend ollama --model qwen2.5:14b --split dev --num-ctx 8192 --repeat 1 --limit 5
python3 -m bench compare runs/<first-run-id> runs/<second-run-id>
```

The Ollama adapter calls native `/api/chat`, sends a JSON schema, temperature, seed, `num_ctx`, `num_predict`, and `keep_alive`, and reads Ollama's native timing and token fields. The prompt is counted with `/api/tokenize` when supported; otherwise a byte-based estimate is used and identified as such. Prompts at or above 90% of `num_ctx` are flagged as likely near truncation. This is a warning heuristic: exact tokenizer counts and silent truncation behavior can vary by Ollama version and model.

If Ollama is unavailable, the run stops with a message naming the endpoint and the `ollama serve` / `ollama pull` actions to check.

## Rented GPU server / vLLM

Run vLLM with its OpenAI-compatible API server on the rented host, and make that server reachable from the machine running this project. Then only change backend settings:

```bash
python3 -m bench run --backend openai \
  --base-url http://GPU-SERVER:8000/v1 \
  --model Qwen/Qwen2.5-14B-Instruct \
  --split dev --repeat 1 --limit 5
```

If the server requires a key, pass `--api-key "$LOCAL_LLM_API_KEY"` or put a key in a private config file. The resolved run config records only whether a key was configured; it never writes the secret. The OpenAI-compatible adapter streams responses to measure time to first token and uses the response `usage` counts when provided. It falls back to character-based prompt-token estimates if usage is absent. Servers differ in support for `seed`, streaming usage, and the JSON object response mode; use a compatible server configuration.

Ollama and OpenAI-compatible endpoints share the same prompt, cases, validation, retries, scoring, and report format. `num_ctx` and `keep_alive` are Ollama-specific; on a vLLM server set the context length and model residency in the server launch configuration. Use the same dataset hash, prompt version, split, limit, output language, and repeat count when comparing hardware or models.

## Configuration and commands

All run options can be supplied as flags or a flat YAML config. Copy `config.example.yaml` and adjust it; CLI flags override config values.

```bash
python3 -m bench run --config config.example.yaml
python3 -m bench run --backend ollama --model qwen2.5:7b --split test
python3 -m bench run --backend ollama --model qwen2.5:7b --split dev --repeat 3
python3 -m bench run --backend ollama --model qwen2.5:7b --split all
python3 -m bench compare runs/<run-id-1> runs/<run-id-2> --output comparison.md
```

Available run settings: `backend`, `base_url`, `api_key`, `model`, `temperature`, `seed`, `num_ctx`, `max_output_tokens`, `keep_alive`, `prompt_version`, `query_version`, `split` (`dev`, `test`, or `all`), `output_language`, `repeat`, and `limit`. The default language for generated explanations is French. Output verdict codes remain stable English schema values; the Markdown case report also displays French status labels.

## Dataset

`data/controls/` contains eight mock controls covering password strength, administrator MFA, failed-login lockout, log retention, critical patch timing, inbound firewall rules, TLS versions, and periodic access review. `data/evidence/<case_id>/` has two or three policy, export, or distractor files for ordinary cases, including native-style YAML, JSON, INI, CSV, and web-server configuration. There are 30 labeled cases: each control has compliant, partial, and non-compliant examples, and six additional insufficient-evidence examples. The test split has 10 cases, covering all four statuses; the remaining 20 are dev. About 30% of examples are French, several mix French and English, and the rest are English.

The mock cases include policy/configuration contradictions, irrelevant distractors, embedded prompt-injection text, and numeric traps such as 90 versus 30 days, TLS 1.0 enabled alongside TLS 1.2, and an unrestricted source on a single firewall port. `data/labels.yaml` includes short rationales for human review. The runner never passes these labels or rationales to the model.

To add a case, create its evidence folder, add the control and evidence filenames, status, split, language, tags, and rationale to `data/labels.yaml`, then run `python3 -m bench validate-data`. To add a control, create a YAML file in `data/controls/` with the documented fields and label evidence cases for it.

## Artifacts and metrics

Each run creates `runs/<run_id>/` with:

- `config.yaml`: resolved options, with API-key value redacted.
- `environment.json`: model/backend identity where exposed, OS, CPU, RAM, GPU, Python, git commit, prompt version, and the stable dataset hash.
- `results.jsonl`: one structured record per case repetition, including raw response, retries, quote validation, token counts, native timings, and truncation flag.
- `metrics.json`: accuracy, confusion matrix, per-class precision/recall, false reassurance and over-strict counts, JSON/schema validity, quote validity, injection resistance, language/tag breakdowns, confidence, performance, warm-up, and sampled resources.
- `report.md` and `cases/<case_id>.md` / `.json`: run summary and human-reviewable case details.

Performance measurements include wall latency, model load time, prompt and output tokens, prompt-processing and generation tokens/second, and time to first token when available. A throwaway warm-up is excluded from timed case latency and reported separately. Resource sampling runs in a background thread at about one-second intervals for host CPU and used RAM, discoverable Ollama server CPU/RSS, and NVIDIA utilization/VRAM through `nvidia-smi`. Missing GPU tooling is reported in the metrics and does not stop a CPU-only run. Peak RAM is system RAM used (not model-process RSS); Ollama server RSS is reported separately when the process can be found.

Latency distributions use wall time across all attempts for each repetition; warm-up is excluded. Throughput uses completed case repetitions per timed minute, and the 300-control projection extrapolates that rate. Repeats count as additional inferences in metrics. Initial/final JSON validity measures parsing; schema-valid rates are reported separately. Failed final outputs count as wrong for overall verdict accuracy and are omitted from the four-by-four confusion matrix, with a separate invalid-output count. Quote validity counts quoted passages only, so a response that returns no quotes has no quote-rate denominator.

## Design decisions and limitations

- The harness uses `httpx`, `pydantic`, `PyYAML`, `psutil`, and `numpy` at runtime. There are no model framework abstractions or hosted API calls.
- The prompt is versioned as `prompts/eval_v1.md`. Evidence is serialized as filename/content JSON and delimited in the user message; the system message says to treat it as untrusted data and ignore instructions embedded in evidence.
- The output uses a Pydantic schema. Ollama receives its JSON Schema directly; the compatible API receives JSON-object mode and is also validated locally. One repair call is made after malformed JSON or schema failure. Persistent failure becomes `invalid_output`.
- Quote checking normalizes Unicode, case, whitespace, and common typographic quotes before checking for a substring in the named file. This catches many formatting-only differences, but paraphrases do not pass.
- The base dataset remains byte-for-byte unchanged and keeps its existing hash. Model inference itself is only deterministic where the backend honors temperature and seed. Different servers can tokenize, stream, and report usage differently.
- For self-hosted OpenAI-compatible servers there is no universal API for version, quantization, model digest, GPU device, or model load time. Such fields are recorded when available; otherwise the report says they were not reported. Wall time and `usage` are used where native timing details are missing.
- NVIDIA metrics require `nvidia-smi`. Other accelerators are not sampled. System CPU and RAM sampling includes unrelated host activity; rented server monitoring and power measurements are outside scope.
- This is a small synthetic benchmark, not a validated estimate of real audit quality. It does not assess every language, document format, control interpretation, prompt-injection strategy, or production workload. A human auditor must validate each proposed result.

## Heavy evidence tiers

`data/heavy/` is generated, reproducible evidence and is ignored by Git; `data/labels_heavy.yaml` is tracked. Heavy generation never calls a model or uses the network. The default estimator is UTF-8 bytes divided by four; it is a sizing estimate, not an exact tokenizer.

```bash
python3 -m bench generate-heavy-data --seed 1729
python3 -m bench validate-data --dataset heavy
python3 -m bench data-stats --dataset heavy
```

The generator creates M (~8k tokens/case), L (~16k), and XL (~32k) variants. Scorable base cases are paired across all three tiers; insufficient-evidence cases have M/L pairs. The current generated set has 92 cases and 730 files. Labels include per-file token estimates, exact gold passages, needle depth, `paired_with`, split, language, and tags. Eight additional adversarial cases cover superseded and draft records, a temporary waiver, buried config facts, a 2,000-row CSV, a near-duplicate number, deep prompt injection, and related but insufficient evidence. The separate heavy dataset hash includes heavy labels, controls, and generated evidence; the base hash is unchanged.

A bilingual pool of 80 handwritten topical blocks supplies realistic adjacent material. A per-control regex denylist checks every bulk file to prevent filler from introducing decisive settings. Tier tolerance is ±15%. `--force` regenerates the heavy tree; changing its seed requires `--force`. Use `--bytes-per-token` to change the estimator consistently.

Heavy runs default to tier M when `--dataset heavy` is selected. Choose one tier first, and use filters/time controls before attempting L or XL on a laptop:

```bash
python3 -m bench run --dataset heavy --tier M --backend ollama --model qwen2.5:7b --split dev --limit 5 --dry-run --assume-prompt-tps 14 --assume-gen-tps 8
python3 -m bench run --dataset heavy --tier M --backend ollama --model qwen2.5:7b --split dev --limit 5 --context-mode full --max-minutes 30 --case-timeout 900
```

The runner also accepts `--control`, comma-separated `--status`, `--repeat`, `--resume <run-id>`, and `--num-ctx auto`. `--max-minutes` stops between model calls and writes a partial report; `--case-timeout` records a timeout and proceeds. Results are appended and flushed after each repetition. Resume skips cases with completed case JSON artifacts. A dry run estimates both full and retrieval prompt sizes and projects time using the latest same-model speeds, or the explicit `--assume-prompt-tps` / `--assume-gen-tps` values. It warns if projected work exceeds one hour. `auto` chooses one constant context for the selected run, rounded up to 1,024 tokens with a configurable `--num-ctx-auto-margin`.

## Retrieval and embedding evaluation

Retrieval indexes only each case's own evidence, so chunks from one case cannot answer another. Markdown is split around heading/paragraph structure; configs use section/line windows; CSV uses row groups with a repeated header stored as metadata. Every chunk records exact source text, offsets, lines, filename, and heading path. CSV header metadata is not treated as a quote. Embeddings are normalized and cached in SQLite at `.cache/retrieval.sqlite3` by model and chunk-content hash. Dense cosine, a small in-process BM25 implementation, and reciprocal-rank fusion are available; there is no vector database service.

The default embedding model is multilingual `bge-m3` through Ollama. Pull it once before indexing (`ollama pull bge-m3`). An OpenAI-compatible embedding endpoint, alternate model, and optional query/passage prefixes can be set with CLI flags. BM25 can run without an embedding model. The retrieval query uses the control's title, description, criteria, and expected-evidence list, never its ID.

```bash
# Build the dense index (embedding work is cached)
python3 -m bench index --dataset heavy --embed-model bge-m3 --chunk-tokens 400 --overlap 60

# Fast offline-from-the-LLM retrieval evaluation; this calls the local embedding endpoint only
python3 -m bench eval-retrieval --dataset heavy --retriever hybrid --top-k 8 --limit 5
python3 -m bench eval-retrieval --dataset heavy --retriever hybrid --sweep

# Compare identical M cases in both prompt modes
python3 -m bench run --dataset heavy --tier M --backend ollama --model qwen2.5:7b --split dev --limit 5 --context-mode full
python3 -m bench run --dataset heavy --tier M --backend ollama --model qwen2.5:7b --split dev --limit 5 --context-mode retrieval --retriever hybrid --top-k 8 --embed-model bge-m3
```

`eval-retrieval` reports gold-passage recall@k, first-hit MRR, and assembled context tokens overall and by tier, language, control, and tag; `--sweep` covers 200/400/800-token chunks, k=3/5/8/12, and dense/BM25/hybrid. It writes Markdown and JSON under `runs/` and makes no LLM calls. `query_v1` is a versioned plain-text query template and can be replaced with another `query_*.md` file selected by `--query-version`. Retrieval runs record selected chunk IDs and scores, tokens sent, query embedding and retrieval time separately from LLM time, whether gold passages reached the final context, and a `retrieval_miss` / `llm_error` / `ok` attribution. Quote checking always uses the original source files.

Choose retrieval settings by looking at both recall and context size. A retrieval miss means the LLM never saw the labeled support; an `llm_error` means all labeled gold passages were present but the verdict still missed. High recall does not guarantee a correct verdict, and labels only assess this synthetic evidence set.

## Measurement additions

Benchmark requests prepend a fresh random nonce to the system prompt by default (`--no-prompt-cache`) to avoid reusing the same Ollama prefix across cases. This changes the prompt slightly and reduces server-side prefix-cache speedups; pass `--allow-prompt-cache` only when measuring a cache-enabled production pattern. The runner independently counts expected prompt tokens using Ollama's tokenizer endpoint where available, compares them with reported prompt-evaluation tokens, and flags `prefix_cached` when reported work is less than 70% of expected. Cached cases do not contribute to mean prompt tokens/second; their case report says `n/a (cached prefix)`.

Reports include model-load, prompt-processing, and generation latency shares; phase and total timing; mean prompt tokens alongside latency; confidence buckets and a warning when confidence does not separate correct from incorrect outcomes; needle-position accuracy for full-context runs; and per-tier/context-mode accuracy, dangerous false reassurance, quote validity, latency, throughput, prompt/generation rates, RAM/VRAM, and projected 300-control hours. `compare` adds scaling and paired S/M/L/XL tables, and warns when dataset hashes, evaluation/query prompt versions, or cache policies differ. `--resume <run-id>` inherits the saved run settings, accepts explicit flag overrides, skips complete cases, and continues missing repetitions. It retains case results and cumulative timed duration; for interrupted runs without a prior metrics file, completed per-case wall times provide the prior-duration estimate. Resource sampling for a resumed process is only from the resumed segment. Legacy runs created before prefix-cache detection are marked as such in comparisons because their prompt speeds may include cached-prefix artifacts.

Before warm-up, the runner makes a best-effort RAM warning from the reported model file size plus a rough KV-cache allowance. This is only a warning heuristic. `num_ctx auto` is constant for a run to avoid Ollama reloads. A prompt at or above 90% of context, or estimated larger than context, is marked likely truncated; server tokenizer behavior and context-shift behavior vary.

## Recommended experiment order

1. Run `eval-retrieval --sweep` on a small subset first, then the full heavy set once the embedding cache is warm.
2. Compare full and retrieval on tier M with `qwen2.5:7b`, using the same split, limit, cases, output language, and repeat count.
3. Repeat those modes on the rented GPU for L and XL with larger models, using an OpenAI-compatible vLLM endpoint. Preserve dataset hash, prompt version, retriever/chunk settings, and filters when making each comparison.

## Label review

`LABEL_REVIEW.md` documents the password-partial review, other ambiguous labels, and a proposed status change for the TLS partial case. The proposal does not modify `data/labels.yaml`; label changes remain an explicit human decision.

## Additional limitations

- The byte-based token estimator used for generated tier sizing can differ from a model tokenizer, especially for French text, JSON punctuation, and CSV. Run prompt tokenization against the chosen backend before drawing hardware conclusions.
- BM25 is intentionally small and has no stemming; dense embeddings and retrieval rankings depend on the configured model. No reranker is included.
- Gold passages are hand-labeled retrieval targets. The synthetic labels, generated filler, and local model results are not a substitute for evaluating realistic client evidence or auditor judgments.
- Query embedding and offline index-build time are reported separately; index-build time is not included in timed LLM case latency. Query embedding is included in end-to-end retrieval throughput.
- RAM sampling is system-wide and can include unrelated activity. GPU sampling currently relies on `nvidia-smi`; other accelerators and server-side vLLM process memory are not queried remotely.
