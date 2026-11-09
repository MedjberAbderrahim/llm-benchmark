from __future__ import annotations

import json
from pathlib import Path

import yaml

from bench.backends import Backend, BackendError, Completion
from bench.chunking import chunk_text
from bench.data_generation import build_dataset
from bench.embeddings import HashEmbeddingBackend
from bench.heavy_data import (DENYLISTS, generate_heavy_dataset, heavy_dataset_hash,
                              validate_filler_text, validate_heavy_dataset)
from bench.retrieval import (IndexStore, bm25_scores, build_index, build_query, data_hash, gold_hit,
                             reciprocal_rank_fusion, tokenize)
from bench.retrieval_eval import evaluate_retrieval
from bench.runner import (_check_quotes, _completed_case_ids, _detect_prefix_cache,
                          _failure_attribution, _make_record, _project_seconds, compare_runs,
                          resolve_config, run_benchmark)
import bench.runner as runner_module

ROOT = Path(__file__).resolve().parents[1]


def test_chunker_ranges_are_lossless_and_exact_with_overlap() -> None:
    source = "# Policy\n\nIntro text.\n\n## Access\n" + "A long source line with details.\n" * 12 + "\nFinal note.\n"
    chunks = chunk_text("policy.md", source, target_tokens=8, overlap_tokens=2, min_chunk_tokens=1)
    assert len(chunks) > 2
    covered = [False] * len(source)
    for chunk in chunks:
        assert chunk.text == source[chunk.start_char:chunk.end_char]
        assert chunk.start_line == source[:chunk.start_char].count("\n") + 1
        expected_end_line = source[:chunk.end_char].count("\n")
        if chunk.end_char > chunk.start_char and not source[:chunk.end_char].endswith("\n"):
            expected_end_line += 1
        assert chunk.end_line == max(chunk.start_line, expected_end_line)
        for position in range(chunk.start_char, chunk.end_char):
            covered[position] = True
    assert all(covered)
    assert chunks[0].heading_path == ("Policy",)
    assert any(chunk.heading_path == ("Policy", "Access") for chunk in chunks)


def test_csv_header_is_metadata_and_quote_check_uses_original() -> None:
    source = "account,decision,state\na-1,remove,pending\na-2,retain,done\n"
    chunks = chunk_text("review.csv", source, target_tokens=2, overlap_tokens=0, min_chunk_tokens=1)
    assert chunks and all(chunk.header == "account,decision,state" for chunk in chunks)
    assert all("account,decision,state" not in chunk.text for chunk in chunks)
    assert all(chunk.text == source[chunk.start_char:chunk.end_char] for chunk in chunks)
    from bench.schemas import EvaluationResponse
    output = EvaluationResponse.model_validate({"status": "partial", "justification": "One pending removal.",
        "criteria_assessment": [], "quotes": [{"file": "review.csv", "text": "account,decision,state"}],
        "recommendation": "Close the action.", "confidence": 0.8})
    checked, valid = _check_quotes(output, {"review.csv": source})
    assert valid == 1 and checked[0]["valid"]


def test_bm25_tokenizer_retains_numbers_ips_tls_and_accents() -> None:
    tokens = tokenize("TLS1.2 uses 90 days; permit 0.0.0.0/0; café accès")
    assert "tls1.2" in tokens
    assert "90" in tokens
    assert "0.0.0.0/0" in tokens
    assert "café" in tokens and "accès" in tokens
    scores = bm25_scores("TLS1.2 90", ["TLS1.2 for 90 days", "unrelated backup note"])
    assert scores[0] > scores[1]


def test_rrf_and_gold_passage_hit() -> None:
    fused = reciprocal_rank_fusion([["a", "b"], ["b", "c"]], k=60)
    assert fused[0][0] == "b"
    assert gold_hit("minimum_length = 14", "prefix minimum_length = 14; suffix")
    assert gold_hit("minimum_length = 14", "minimum_length = 14; extra", threshold=.8)
    assert not gold_hit("minimum_length = 14", "retention_days = 90")
    query = build_query({"id": "DO_NOT_INCLUDE", "title": "Password length", "description": "A policy",
                         "evaluation_criteria": ["minimum length"], "expected_evidence": ["config export"]},
                        "{{TITLE}} {{DESCRIPTION}} {{EVALUATION_CRITERIA}} {{EXPECTED_EVIDENCE}}")
    assert "Password length" in query and "DO_NOT_INCLUDE" not in query


def test_measurement_helpers_and_failure_attribution() -> None:
    assert _detect_prefix_cache(1000, 600)
    assert not _detect_prefix_cache(1000, 800)
    assert _project_seconds(1000, 100, 10, 5, 2) == 240
    assert _failure_attribution("partial", False, False) == "retrieval_miss"
    assert _failure_attribution("partial", True, False) == "llm_error"
    assert _failure_attribution("partial", True, True) == "ok"
    assert _failure_attribution("insufficient_evidence", False, True) == "n/a"
    assert _failure_attribution("partial", False, False, gold_passage_count=0) == "n/a"


def test_resume_skips_cases_with_case_artifacts(tmp_path: Path) -> None:
    (tmp_path / "cases").mkdir()
    (tmp_path / "cases" / "case-a.json").write_text(
        json.dumps({"repetitions": [{"repetition": 1}]}), encoding="utf-8")
    selected = [{"case_id": "case-a"}, {"case_id": "case-b"}]
    assert _completed_case_ids(tmp_path, selected, repeat=1) == {"case-a"}
    assert _completed_case_ids(tmp_path, selected, repeat=2) == set()


def test_resume_inherits_saved_run_settings_and_allows_explicit_override(tmp_path: Path) -> None:
    run_dir = tmp_path / "saved-run"
    run_dir.mkdir()
    (run_dir / "config.yaml").write_text(yaml.safe_dump({"backend": "openai", "model": "saved-model",
        "dataset": "heavy", "tier": "L", "split": "test", "limit": 4, "repeat": 2,
        "context_mode": "retrieval", "retriever": "bm25", "api_key_configured": False}), encoding="utf-8")
    config = resolve_config(None, {"resume": str(run_dir), "model": "override-model"})
    assert config["backend"] == "openai" and config["dataset"] == "heavy"
    assert config["tier"] == "L" and config["split"] == "test" and config["limit"] == 4
    assert config["repeat"] == 2 and config["context_mode"] == "retrieval"
    assert config["model"] == "override-model"


def test_config_rejects_nonpositive_budgets_and_speeds() -> None:
    import pytest
    with pytest.raises(ValueError, match="max_minutes must be positive"):
        resolve_config(None, {"model": "fake", "max_minutes": 0})
    with pytest.raises(ValueError, match="case_timeout must be positive"):
        resolve_config(None, {"model": "fake", "case_timeout": -1})
    with pytest.raises(ValueError, match="assume_prompt_tps must be positive"):
        resolve_config(None, {"model": "fake", "assume_prompt_tps": 0})


class _TimeoutLLM(Backend):
    def generate(self, messages: list[dict[str, str]]) -> Completion:
        raise BackendError("synthetic request timed out")

    def warmup(self) -> Completion:
        return Completion("OK", 0.001, None, {})

    def prompt_token_count(self, messages: list[dict[str, str]]) -> tuple[int, str]:
        return 100, "test-estimator"


def test_case_timeout_is_recorded_and_run_continues_to_report(tmp_path: Path, monkeypatch) -> None:
    build_dataset(tmp_path)
    (tmp_path / "prompts").mkdir()
    (tmp_path / "prompts" / "eval_v1.md").write_text(
        (ROOT / "prompts" / "eval_v1.md").read_text(encoding="utf-8"), encoding="utf-8")
    monkeypatch.setattr(runner_module, "create_backend", lambda _config: _TimeoutLLM())
    config = resolve_config(None, {"model": "fake-timeout", "split": "all", "limit": 1,
                                   "case_timeout": 1})
    run_dir = run_benchmark(tmp_path, config)
    row = json.loads((run_dir / "results.jsonl").read_text(encoding="utf-8").splitlines()[0])
    metrics = json.loads((run_dir / "metrics.json").read_text(encoding="utf-8"))
    assert row["status"] == "timeout" and not row["matches_expected"]
    assert metrics["partial_run"] is False


def test_heavy_labels_validate_deterministically_without_changing_base_hash(tmp_path: Path) -> None:
    assert build_dataset(tmp_path) == 30
    from bench.util import dataset_hash
    base_before = dataset_hash(tmp_path)
    assert generate_heavy_dataset(tmp_path, seed=91) == 92
    digest1 = heavy_dataset_hash(tmp_path)
    assert validate_heavy_dataset(tmp_path) == 92
    labels = yaml.safe_load((tmp_path / "data" / "labels_heavy.yaml").read_text(encoding="utf-8"))
    assert {row["tier"] for row in labels} == {"M", "L", "XL"}
    for row in labels:
        target = {"M": 8000, "L": 16000, "XL": 32000}[row["tier"]]
        assert target * .85 <= row["approx_tokens"]["total"] <= target * 1.15
        case_root = tmp_path / "data" / "heavy" / "evidence" / row["case_id"]
        for passage in row["gold_passages"]:
            assert passage["text"] in (case_root / passage["file"]).read_text(encoding="utf-8")
    assert validate_filler_text("MOCK-PWD-01", "minimum_length = 8")
    assert not validate_filler_text("MOCK-PWD-01", "Backup media is inventoried by the operations team.")
    assert dataset_hash(tmp_path) == base_before
    generate_heavy_dataset(tmp_path, seed=91, force=True)
    assert heavy_dataset_hash(tmp_path) == digest1


class _FakeLLM(Backend):
    def generate(self, messages: list[dict[str, str]]) -> Completion:
        payload = {"status": "compliant", "justification": "The effective setting is supported.",
                   "criteria_assessment": [], "quotes": [{"file": "effective-policy.ini", "text": "minimum_length = 14"}],
                   "recommendation": "", "confidence": 0.8}
        return Completion(json.dumps(payload), 0.01, 0.003,
                          {"prompt_tokens": 80, "completion_tokens": 20})

    def prompt_token_count(self, messages: list[dict[str, str]]) -> tuple[int, str]:
        return 100, "test-estimator"


class _PrefixCachedFakeLLM(_FakeLLM):
    def generate(self, messages: list[dict[str, str]]) -> Completion:
        completion = super().generate(messages)
        completion.metrics = {"prompt_eval_count": 40, "prompt_eval_duration": 1_000_000_000,
                              "eval_count": 20, "eval_duration": 1_000_000_000,
                              "total_duration": 2_000_000_000, "load_duration": 0}
        return completion


def test_fake_embedding_index_and_fake_llm_record_work_offline(tmp_path: Path) -> None:
    build_dataset(tmp_path)
    labels = yaml.safe_load((tmp_path / "data" / "labels.yaml").read_text(encoding="utf-8"))
    label = next(row for row in labels if row["case_id"] == "mock-pwd-01-compliant-01")
    control = yaml.safe_load((tmp_path / "data" / "controls" / f"{label['control_id']}.yaml").read_text(encoding="utf-8"))
    evidence_root = tmp_path / "data" / "evidence" / label["case_id"]
    evidence = {name: (evidence_root / name).read_text(encoding="utf-8") for name in label["evidence_files"]}
    config = resolve_config(None, {"model": "fake", "num_ctx": 8192})
    # The temporary root supplies the generated case data; prompt templates
    # remain the project-owned, versioned templates under ROOT/prompts.
    record = _make_record(ROOT, _FakeLLM(), config, label, control, evidence, 1)
    assert record["status"] == "compliant" and record["quote_validity"]["rate"] == 1
    cached_record = _make_record(ROOT, _PrefixCachedFakeLLM(), config, label, control, evidence, 1)
    assert cached_record["prefix_cached"] and cached_record["prompt_tokens"] == 100
    assert cached_record["prompt_tokens_reported_by_backend"] == 40
    assert cached_record["prompt_processing_tokens_per_second"] is None

    store_path = tmp_path / "cache.sqlite3"
    embedding = HashEmbeddingBackend(dimension=32)
    info = build_index(tmp_path, "base", embedding, store_path, chunk_tokens=100, overlap=10,
                       case_ids=[label["case_id"]])
    store = IndexStore(store_path)
    chunks = store.get_case_chunks(info["index_key"], label["case_id"])
    assert chunks and all(vector is not None for _, vector in chunks)
    assert store.get_case_chunks(info["index_key"], "another-case") == []
    store.close()


def test_bm25_retrieval_evaluation_runs_without_an_embedding_service(tmp_path: Path) -> None:
    build_dataset(tmp_path)
    (tmp_path / "prompts").mkdir()
    (tmp_path / "prompts" / "query_v1.md").write_text(
        (ROOT / "prompts" / "query_v1.md").read_text(encoding="utf-8"), encoding="utf-8")
    report = evaluate_retrieval(tmp_path, "base", None, tmp_path / ".cache" / "index.sqlite3",
                                retriever="bm25", top_k=3, chunk_tokens=100, overlap=10,
                                token_budget=500, limit=1, query_version="query_v1")
    assert report.exists()
    assert "Recall@k" in report.read_text(encoding="utf-8")
    assert report.with_suffix(".json").exists()


def test_retrieval_sweep_runs_offline_with_hash_embeddings(tmp_path: Path) -> None:
    build_dataset(tmp_path)
    (tmp_path / "prompts").mkdir()
    (tmp_path / "prompts" / "query_v1.md").write_text(
        (ROOT / "prompts" / "query_v1.md").read_text(encoding="utf-8"), encoding="utf-8")
    report = evaluate_retrieval(tmp_path, "base", HashEmbeddingBackend(dimension=24),
                                tmp_path / ".cache" / "sweep.sqlite3", limit=1,
                                sweep=True, query_version="query_v1")
    contents = report.read_text(encoding="utf-8")
    assert "dense" in contents and "bm25" in contents and "hybrid" in contents
    assert "Recall@k" in contents


def test_compare_report_warns_on_incomparable_runs(tmp_path: Path) -> None:
    run_dirs = []
    for name, data_hash in (("one", "hash-a"), ("two", "hash-b")):
        run_dir = tmp_path / "runs" / name
        run_dir.mkdir(parents=True)
        (run_dir / "config.yaml").write_text(yaml.safe_dump({"model": name, "dataset": "base",
            "context_mode": "full", "tier": "S", "no_prompt_cache": True}), encoding="utf-8")
        (run_dir / "environment.json").write_text(json.dumps({"model": name}), encoding="utf-8")
        (run_dir / "metrics.json").write_text(json.dumps({"dataset_hash": data_hash,
            "prompt_version": "eval_v1", "query_version": "query_v1", "tier_set": ["S"],
            "latency_seconds": {}, "resource_metrics": {}}), encoding="utf-8")
        run_dirs.append(run_dir)
    report = compare_runs(run_dirs, tmp_path / "comparison.md")
    assert "different dataset hashes" in report.read_text(encoding="utf-8")
