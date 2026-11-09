from __future__ import annotations

import json
import math
import secrets
import re
import statistics
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from .backends import Backend, BackendError, Completion, create_backend
from .data_generation import validate_dataset
from .resources import ResourceSampler, environment_snapshot
from .schemas import EvaluationResponse
from .scoring import STATUSES, build_metrics
from .util import dataset_hash, normalize_quote, strip_json_fence, write_json
from .heavy_data import heavy_dataset_hash, validate_heavy_dataset
from .retrieval import (IndexStore, assemble_context, build_index, build_query, create_embedding,
                        data_hash as selected_data_hash, gold_hit, index_key, load_labels, retrieve_case)


DEFAULTS: dict[str, Any] = {
    "backend": "ollama", "base_url": "http://localhost:11434", "model": "qwen2.5:7b",
    "api_key": None, "temperature": 0.0, "seed": 42, "num_ctx": 8192,
    "max_output_tokens": 512, "keep_alive": "10m", "prompt_version": "eval_v1",
    "query_version": "query_v1",
    "split": "dev", "output_language": "fr", "repeat": 1, "limit": None,
    "dataset": "base", "context_mode": "full", "retriever": "hybrid", "tier": None,
    "control": None, "status": None, "max_minutes": None, "case_timeout": None,
    "resume": None, "dry_run": False, "assume_prompt_tps": None, "assume_gen_tps": None,
    "no_prompt_cache": True, "num_ctx_auto_margin": 1024,
    "embed_model": "bge-m3", "embed_backend": "ollama", "embed_base_url": None,
    "embed_api_key": None, "chunk_tokens": 400, "overlap": 60, "top_k": 8,
    "context_token_budget": 4000, "context_order": "file", "cache_db": ".cache/retrieval.sqlite3",
}


def resolve_config(config_file: Path | None, overrides: dict[str, Any]) -> dict[str, Any]:
    result = dict(DEFAULTS)
    if config_file:
        loaded = yaml.safe_load(config_file.read_text(encoding="utf-8")) or {}
        if not isinstance(loaded, dict):
            raise ValueError(f"Config file must contain a YAML mapping: {config_file}")
        result.update(loaded)
    explicit = {key: value for key, value in overrides.items() if value is not None}
    resume_value = explicit.get("resume", result.get("resume"))
    if resume_value:
        resume_path = Path(str(resume_value))
        if not resume_path.is_absolute():
            project_root = Path(__file__).resolve().parents[1]
            resume_path = project_root / (resume_path if str(resume_path).startswith("runs/") else Path("runs") / resume_path)
        saved_path = resume_path / "config.yaml"
        if not saved_path.is_file():
            raise ValueError(f"Cannot resume; saved run config does not exist: {saved_path}")
        saved = yaml.safe_load(saved_path.read_text(encoding="utf-8")) or {}
        if not isinstance(saved, dict):
            raise ValueError(f"Saved run config must contain a YAML mapping: {saved_path}")
        for key in DEFAULTS:
            if key in saved:
                result[key] = saved[key]
        if saved.get("api_key_configured") and "api_key" not in explicit and not result.get("api_key"):
            raise ValueError("This run used an API key that is not stored in artifacts; pass --api-key to resume it.")
        if saved.get("embed_api_key_configured") and "embed_api_key" not in explicit and not result.get("embed_api_key"):
            raise ValueError("This run used an embedding API key that is not stored in artifacts; pass --embed-api-key to resume it.")
    result.update(explicit)
    if result["backend"] not in {"ollama", "openai"}:
        raise ValueError("backend must be 'ollama' or 'openai'")
    if result["split"] not in {"dev", "test", "all"}:
        raise ValueError("split must be dev, test, or all")
    if int(result["repeat"]) < 1:
        raise ValueError("repeat must be at least 1")
    if result["num_ctx"] != "auto" and int(result["num_ctx"]) < 256:
        raise ValueError("num_ctx must be at least 256")
    if int(result["max_output_tokens"]) < 1:
        raise ValueError("max_output_tokens must be positive")
    if not result.get("model"):
        raise ValueError("model is required (set --model or model in YAML config)")
    if result.get("limit") is not None and int(result["limit"]) < 1:
        raise ValueError("limit must be positive")
    for key in ("max_minutes", "case_timeout", "assume_prompt_tps", "assume_gen_tps"):
        if result.get(key) is not None and (not math.isfinite(float(result[key])) or float(result[key]) <= 0):
            raise ValueError(f"{key} must be positive when provided")
    if int(result["num_ctx_auto_margin"]) < 0:
        raise ValueError("num_ctx_auto_margin must be non-negative")
    if result["dataset"] not in {"base", "heavy"}:
        raise ValueError("dataset must be base or heavy")
    if result["context_mode"] not in {"full", "retrieval"}:
        raise ValueError("context_mode must be full or retrieval")
    if not result.get("query_version") or not re.fullmatch(r"query_[A-Za-z0-9_.-]+", str(result["query_version"])):
        raise ValueError("query_version must name a versioned query template such as query_v1")
    if result["retriever"] not in {"dense", "bm25", "hybrid"}:
        raise ValueError("retriever must be dense, bm25, or hybrid")
    if result["tier"] is None:
        result["tier"] = "S" if result["dataset"] == "base" else "M"
    if result["tier"] not in {"S", "M", "L", "XL", "all"}:
        raise ValueError("tier must be S, M, L, XL, or all")
    if result["dataset"] == "base" and result["tier"] not in {"S", "all"}:
        raise ValueError("Base data only has tier S")
    if result["dataset"] == "heavy" and result["tier"] == "S":
        raise ValueError("Heavy data has tiers M, L, and XL; choose one or all")
    if result["num_ctx"] != "auto":
        result["num_ctx"] = int(result["num_ctx"])
    for key in ("chunk_tokens", "top_k", "context_token_budget"):
        if int(result[key]) < 1:
            raise ValueError(f"{key} must be positive")
    if int(result["overlap"]) < 0 or int(result["overlap"]) >= int(result["chunk_tokens"]):
        raise ValueError("overlap must be non-negative and less than chunk_tokens")
    return result


def _prompt(root: Path, config: dict[str, Any], control: dict[str, Any], evidence: list[dict[str, str]]) -> list[dict[str, str]]:
    template_path = root / "prompts" / f"{config['prompt_version']}.md"
    if not template_path.is_file():
        raise ValueError(f"Prompt template not found: {template_path}")
    template = template_path.read_text(encoding="utf-8")
    system_part, marker, user_part = template.partition("---USER---")
    if not marker:
        raise ValueError(f"Prompt template must contain ---USER---: {template_path}")
    control_json = json.dumps(control, ensure_ascii=False, indent=2)
    evidence_json = json.dumps(evidence, ensure_ascii=False, indent=2)
    from .schemas import OUTPUT_JSON_SCHEMA
    schema_json = json.dumps(OUTPUT_JSON_SCHEMA, ensure_ascii=False, indent=2)
    replacements = {"{{OUTPUT_LANGUAGE}}": str(config["output_language"]), "{{CONTROL_JSON}}": control_json,
                   "{{EVIDENCE_JSON}}": evidence_json, "{{SCHEMA_JSON}}": schema_json}
    system = system_part.strip()
    user = user_part.strip()
    for key, value in replacements.items():
        system = system.replace(key, value)
        user = user.replace(key, value)
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def _parse(content: str) -> tuple[bool, bool, EvaluationResponse | None, str | None, str | None]:
    try:
        raw = json.loads(strip_json_fence(content))
    except (json.JSONDecodeError, TypeError) as exc:
        return False, False, None, None, str(exc)
    try:
        parsed = EvaluationResponse.model_validate(raw)
        return True, True, parsed, None, None
    except ValidationError as exc:
        return True, False, None, json.dumps(exc.errors(include_url=False), ensure_ascii=False), str(exc)


def _detect_prefix_cache(expected_tokens: int | None, reported_tokens: int | None, threshold: float = 0.70) -> bool:
    return bool(expected_tokens and reported_tokens is not None and reported_tokens < expected_tokens * threshold)


def _project_seconds(prompt_tokens: int, output_tokens: int, prompt_tps: float,
                     generation_tps: float, repeats: int = 1) -> float:
    if prompt_tps <= 0 or generation_tps <= 0 or repeats < 1:
        raise ValueError("Speeds must be positive and repeats must be at least one")
    return (prompt_tokens / prompt_tps + output_tokens / generation_tps) * repeats


def _completed_case_ids(run_dir: Path, selected: list[dict[str, Any]], repeat: int = 1) -> set[str]:
    selected_ids = {row["case_id"] for row in selected}
    completed: set[str] = set()
    for path in (run_dir / "cases").glob("*.json"):
        if path.stem not in selected_ids:
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            repetitions = {int(row.get("repetition", 0)) for row in payload.get("repetitions", [])}
            if len(repetitions) >= repeat:
                completed.add(path.stem)
        except (OSError, ValueError, TypeError):
            continue
    return completed


def _failure_attribution(expected_status: str, all_gold_retrieved: bool, matches_expected: bool,
                         gold_passage_count: int | None = None) -> str:
    if expected_status == "insufficient_evidence" or gold_passage_count == 0:
        return "n/a"
    if not all_gold_retrieved:
        return "retrieval_miss"
    return "ok" if matches_expected else "llm_error"


def _check_quotes(response: EvaluationResponse, evidence: dict[str, str]) -> tuple[list[dict[str, Any]], int]:
    content_by_name = {name: normalize_quote(text) for name, text in evidence.items()}
    result: list[dict[str, Any]] = []
    valid_count = 0
    for quote in response.quotes:
        filename = Path(quote.file).name
        source = content_by_name.get(filename)
        valid = bool(quote.text.strip()) and source is not None and normalize_quote(quote.text) in source
        valid_count += int(valid)
        result.append({"file": quote.file, "text": quote.text, "valid": valid})
    return result, valid_count


def _native_seconds(metrics: dict[str, Any], key: str) -> float | None:
    value = metrics.get(key)
    return float(value) / 1_000_000_000 if isinstance(value, (int, float)) else None


def _make_record(root: Path, backend: Backend, config: dict[str, Any], label: dict[str, Any],
                 control: dict[str, Any], evidence: dict[str, str], repetition: int,
                 retrieval_meta: dict[str, Any] | None = None,
                 original_evidence: dict[str, str] | None = None) -> dict[str, Any]:
    evidence_rows = [{"filename": filename, "content": content} for filename, content in evidence.items()]
    prompt_config = dict(config)
    if config["context_mode"] == "retrieval":
        prompt_config["prompt_version"] = "eval_v2_retrieval"
    messages = _prompt(root, prompt_config, control, evidence_rows)
    request_messages = _request_nonce(messages, config)
    prompt_tokens_estimate, prompt_count_method = backend.prompt_token_count(request_messages)
    prompt_near_limit = prompt_tokens_estimate >= int(config["num_ctx"]) * 0.9
    attempts: list[Completion] = []
    started = time.perf_counter()
    try:
        first = backend.generate(request_messages)
    except BackendError:
        raise
    attempts.append(first)
    initial_json_valid, initial_schema_valid, parsed, schema_error, parse_error = _parse(first.content)
    repair_reason = schema_error or parse_error
    if not initial_schema_valid:
        if config.get("case_timeout"):
            remaining = float(config["case_timeout"]) - (time.perf_counter() - started)
            if remaining <= 0:
                raise BackendError("Case timed out before the JSON repair request could start.")
            backend.set_timeout(remaining)
        repair_messages = messages + [
            {"role": "assistant", "content": first.content},
            {"role": "user", "content": ("Your previous response failed JSON/schema validation. Return valid JSON only, "
              "matching the required schema exactly. Do not add prose or markdown fences. Validation details: "
              + str(repair_reason)[:1800])},
        ]
        repair_messages = _request_nonce(repair_messages, config)
        try:
            second = backend.generate(repair_messages)
        except BackendError:
            raise
        attempts.append(second)
        final_json_valid, final_schema_valid, parsed, _, _ = _parse(second.content)
    else:
        final_json_valid, final_schema_valid = initial_json_valid, initial_schema_valid
    elapsed = time.perf_counter() - started
    raw_final = attempts[-1].content
    raw_response = parsed.model_dump(mode="json") if final_schema_valid and parsed else None
    quote_rows: list[dict[str, Any]] = []
    valid_quotes = 0
    if parsed:
        quote_rows, valid_quotes = _check_quotes(parsed, original_evidence or evidence)
        raw_response["quotes"] = quote_rows
    native = [attempt.metrics for attempt in attempts]
    native_prompt_tokens = sum(int(item.get("prompt_eval_count") or 0) for item in native)
    native_output_tokens = sum(int(item.get("eval_count") or 0) for item in native)
    openai_prompt_tokens = sum(int(item.get("prompt_tokens") or 0) for item in native)
    openai_output_tokens = sum(int(item.get("completion_tokens") or 0) for item in native)
    prompt_tokens = native_prompt_tokens or openai_prompt_tokens or prompt_tokens_estimate
    output_tokens = native_output_tokens or openai_output_tokens
    if not output_tokens:
        output_tokens = max(1, len(raw_final.encode("utf-8")) // 4) if raw_final else 0
    prompt_durations = [v for v in (_native_seconds(item, "prompt_eval_duration") for item in native) if v is not None]
    generation_durations = [v for v in (_native_seconds(item, "eval_duration") for item in native) if v is not None]
    load_durations = [v for v in (_native_seconds(item, "load_duration") for item in native) if v is not None]
    native_total = [v for v in (_native_seconds(item, "total_duration") for item in native) if v is not None]
    prompt_time = sum(prompt_durations) if prompt_durations else None
    generation_time = sum(generation_durations) if generation_durations else None
    load_time = sum(load_durations) if load_durations else None
    first_native_prompt = int(native[0].get("prompt_eval_count") or 0) if native else 0
    prefix_cached = _detect_prefix_cache(prompt_tokens_estimate, first_native_prompt)
    if prefix_cached:
        # Ollama reports only newly evaluated tokens when it reuses a prefix;
        # retain the independent full-prompt estimate for input-size metrics.
        prompt_tokens = prompt_tokens_estimate
        prompt_time = None
    prompt_speed = prompt_tokens / prompt_time if prompt_time and prompt_time > 0 else None
    generation_speed = native_output_tokens / generation_time if generation_time and generation_time > 0 else None
    ttft_values = [attempt.time_to_first_token_seconds for attempt in attempts if attempt.time_to_first_token_seconds is not None]
    ttft = ttft_values[0] if ttft_values else None
    if prompt_speed is None and not prefix_cached and ttft and ttft > 0:
        prompt_speed = prompt_tokens / ttft
    if generation_speed is None and ttft is not None and elapsed > ttft:
        generation_speed = output_tokens / (elapsed - ttft)
    prompt_actual_near_limit = native_prompt_tokens >= int(config["num_ctx"]) * 0.9
    exceeds_context = prompt_tokens_estimate > int(config["num_ctx"])
    likely_truncated = bool(prompt_near_limit or prompt_actual_near_limit or exceeds_context)
    status = parsed.status.value if final_schema_valid and parsed else "invalid_output"
    expected = label["expected_status"]
    wall_total = sum(attempt.wall_seconds for attempt in attempts)
    phase_denominator = wall_total if wall_total > 0 else 1.0
    phase_shares = {"model_load": (load_time / phase_denominator) if load_time is not None else None,
                    "prompt_processing": (sum(prompt_durations) / phase_denominator) if prompt_durations else None,
                    "generation": (sum(generation_durations) / phase_denominator) if generation_durations else None}
    record = {
        "case_id": label["case_id"], "control_id": label["control_id"], "repetition": repetition,
        "expected_status": expected, "status": status, "matches_expected": status == expected,
        "confidence": parsed.confidence if parsed else None,
        "justification": parsed.justification if parsed else None,
        "criteria_assessment": [item.model_dump(mode="json") for item in parsed.criteria_assessment] if parsed else [],
        "quotes": quote_rows, "recommendation": parsed.recommendation if parsed else None,
        "raw_output_initial": first.content, "raw_output_final": raw_final,
        "initial_json_valid": initial_json_valid, "initial_schema_valid": initial_schema_valid,
        "final_json_valid": final_json_valid, "final_schema_valid": final_schema_valid,
        "retry_count": len(attempts) - 1,
        "quote_validity": {"valid": valid_quotes, "total": len(quote_rows),
                           "rate": valid_quotes / len(quote_rows) if quote_rows else None},
        "wall_clock_total_seconds": wall_total,
        "wall_clock_elapsed_seconds": elapsed,
        "model_reported_total_seconds": sum(native_total) if native_total else None,
        "model_load_seconds": load_time,
        "prompt_tokens": prompt_tokens, "output_tokens": output_tokens,
        "prompt_token_count_method": "ollama_native" if native_prompt_tokens else ("openai_usage" if openai_prompt_tokens else prompt_count_method),
        "prompt_processing_seconds": prompt_time,
        "prompt_processing_tokens_per_second": prompt_speed,
        "generation_seconds": generation_time,
        "generation_tokens_per_second": generation_speed,
        "time_to_first_token_seconds": ttft,
        "native_metrics_by_attempt": native,
        "prompt_tokens_estimated_before_call": prompt_tokens_estimate,
        "prompt_tokens_reported_by_backend": native_prompt_tokens or openai_prompt_tokens or None,
        "prefix_cached": prefix_cached,
        "prefix_cache_detection": "reported prompt tokens < 70% of independently counted prompt tokens",
        "phase_latency_shares": phase_shares,
        "likely_truncated": likely_truncated,
        "prompt_exceeds_num_ctx": exceeds_context,
        "num_ctx": config["num_ctx"],
        "prompt_version": prompt_config["prompt_version"], "language": label["language"], "tags": label["tags"],
        "tier": label.get("tier", "S"), "paired_with": label.get("paired_with"),
        "needle_position": label.get("needle_position", {}).get("bucket", "none"),
        "context_mode": config["context_mode"],
        "retrieval": retrieval_meta or {},
    }
    return record


def _request_nonce(messages: list[dict[str, str]], config: dict[str, Any]) -> list[dict[str, str]]:
    result = [dict(message) for message in messages]
    if config.get("no_prompt_cache", True) and result:
        result[0]["content"] = f"Benchmark request nonce: {secrets.token_hex(16)}\n" + result[0]["content"]
    return result


STATUS_FR = {"compliant": "Conforme", "partial": "Partiellement conforme",
             "non_compliant": "Non conforme", "insufficient_evidence": "À vérifier / En attente de preuve",
             "invalid_output": "Sortie invalide", "timeout": "Délai dépassé"}


def _case_markdown(label: dict[str, Any], records: list[dict[str, Any]], control: dict[str, Any]) -> str:
    lines = [f"# {label['case_id']}", "", f"- Control: **{control['id']} — {control['title']}**",
             f"- Expected status: **{STATUS_FR[label['expected_status']]}** (`{label['expected_status']}`)",
             f"- Dataset rationale (human review only): {label['rationale']}", f"- Language: {label['language']}",
             f"- Tags: {', '.join(label['tags']) if label['tags'] else 'none'}", "", "## Control criteria", ""]
    lines.extend(f"- {criterion}" for criterion in control["evaluation_criteria"])
    for row in records:
        lines += ["", f"## Repetition {row['repetition']}", "",
                  f"- Verdict: **{STATUS_FR[row['status']]}** (`{row['status']}`)",
                  f"- Expected match: **{'yes' if row['matches_expected'] else 'no'}**",
                  f"- Confidence: {row['confidence'] if row['confidence'] is not None else 'unavailable'}",
                  f"- Retry count: {row['retry_count']}; likely truncation: {row['likely_truncated']}",
                  f"- Latency: {row['wall_clock_total_seconds']:.3f} s; prompt/output tokens: {row['prompt_tokens']}/{row['output_tokens']}", "",
                  f"- Backend prompt tokens: {row.get('prompt_tokens_reported_by_backend') if row.get('prompt_tokens_reported_by_backend') is not None else 'unavailable'}; independent estimate: {row.get('prompt_tokens_estimated_before_call')}", "",
                  f"- Prompt processing speed: {'n/a (cached prefix)' if row.get('prefix_cached') else _fmt(row.get('prompt_processing_tokens_per_second'), 1) + ' tokens/s'}; generation speed: {_fmt(row.get('generation_tokens_per_second'), 1)} tokens/s", "",
                  "### Justification", "", row["justification"] or "No schema-valid justification was returned.", "",
                  "### Criterion assessment", ""]
        if row["criteria_assessment"]:
            lines += [f"- **{item['met']}** — {item['criterion']}: {item['note']}" for item in row["criteria_assessment"]]
        else:
            lines.append("- Unavailable")
        lines += ["", "### Quotes", ""]
        if row["quotes"]:
            lines += [f"- {'✅' if quote['valid'] else '❌ INVALID'} `{quote['file']}`: {quote['text']}" for quote in row["quotes"]]
        else:
            lines.append("- No quotes returned.")
        lines += ["", f"### Recommendation", "", row["recommendation"] or "Not available."]
        retrieval = row.get("retrieval") or {}
        if retrieval:
            lines += ["", "### Retrieval", "", f"- Chunks: {len(retrieval.get('retrieved_chunks', []))}; tokens sent: {retrieval.get('tokens_sent', 'n/a')}",
                      f"- Retrieval / query embedding: {_fmt(retrieval.get('retrieval_seconds'))} s / {_fmt(retrieval.get('embedding_seconds'))} s",
                      f"- Gold passages in context: {retrieval.get('gold_passages_retrieved', 0)}/{retrieval.get('gold_passage_count', 0)}",
                      f"- Attribution: {retrieval.get('failure_attribution', 'n/a')}"]
    return "\n".join(lines) + "\n"


def _retrieval_evidence(context: list[dict[str, Any]]) -> dict[str, str]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for item in context:
        grouped.setdefault(str(item["filename"]), []).append(item)
    result: dict[str, str] = {}
    for filename, items in grouped.items():
        parts = []
        for item in items:
            path = " > ".join(item.get("heading_path", [])) or "(section not identified)"
            parts.append(f"[Retrieved excerpt: lines {item['start_line']}-{item['end_line']}; heading: {path}]\n")
            if item.get("header"):
                parts.append(f"CSV header metadata (not a source quote): {item['header']}\n")
            parts.append(str(item["source_text"]))
        result[filename] = "\n\n".join(parts)
    return result


def _timeout_record(label: dict[str, Any], repetition: int, retrieval_meta: dict[str, Any], elapsed: float) -> dict[str, Any]:
    return {"case_id": label["case_id"], "control_id": label["control_id"], "repetition": repetition,
            "expected_status": label["expected_status"], "status": "timeout", "matches_expected": False,
            "confidence": None, "justification": None, "criteria_assessment": [], "quotes": [],
            "recommendation": None, "raw_output_initial": None, "raw_output_final": None,
            "initial_json_valid": False, "initial_schema_valid": False, "final_json_valid": False,
            "final_schema_valid": False, "retry_count": 0, "quote_validity": {"valid": 0, "total": 0, "rate": None},
            "wall_clock_total_seconds": elapsed, "wall_clock_elapsed_seconds": elapsed,
            "model_reported_total_seconds": None, "model_load_seconds": None, "prompt_tokens": 0,
            "output_tokens": 0, "prompt_token_count_method": "timeout", "prompt_processing_seconds": None,
            "prompt_processing_tokens_per_second": None, "generation_seconds": None,
            "generation_tokens_per_second": None, "time_to_first_token_seconds": None,
            "native_metrics_by_attempt": [], "prompt_tokens_estimated_before_call": None,
            "prompt_tokens_reported_by_backend": None, "prefix_cached": False, "phase_latency_shares": {},
            "likely_truncated": False, "prompt_exceeds_num_ctx": False, "num_ctx": None,
            "prompt_version": "eval_v2_retrieval" if retrieval_meta else "eval_v1",
            "language": label["language"], "tags": label["tags"], "tier": label.get("tier", "S"),
            "paired_with": label.get("paired_with"), "needle_position": label.get("needle_position", {}).get("bucket", "none"),
            "context_mode": "retrieval" if retrieval_meta else "full", "retrieval": retrieval_meta}


def _latest_speeds(root: Path, backend: str, model: str) -> tuple[float | None, float | None]:
    candidates = []
    for metrics_path in (root / "runs").glob("*/metrics.json"):
        config_path = metrics_path.parent / "config.yaml"
        try:
            config = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
            metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
            if config.get("backend") == backend and config.get("model") == model:
                candidates.append((metrics_path.stat().st_mtime, metrics))
        except (OSError, ValueError, yaml.YAMLError):
            continue
    if not candidates:
        return None, None
    metrics = max(candidates, key=lambda item: item[0])[1]
    return metrics.get("mean_prompt_processing_tokens_per_second"), metrics.get("mean_generation_tokens_per_second")


def _dry_run(root: Path, config: dict[str, Any], selected: list[dict[str, Any]], controls: dict[str, Any]) -> None:
    from .chunking import estimate_tokens
    prompt_tps = config.get("assume_prompt_tps")
    gen_tps = config.get("assume_gen_tps")
    if prompt_tps is None or gen_tps is None:
        recent_prompt, recent_gen = _latest_speeds(root, config["backend"], config["model"])
        prompt_tps = prompt_tps or recent_prompt
        gen_tps = gen_tps or recent_gen
    if not prompt_tps or not gen_tps:
        print("No recent uncached speed result found; pass --assume-prompt-tps and --assume-gen-tps for a time projection.")
    largest = 0
    selected_estimates: list[int] = []
    for label in selected:
        evidence_root = root / "data" / ("heavy/evidence" if config["dataset"] == "heavy" else "evidence") / label["case_id"]
        content = {name: (evidence_root / name).read_text(encoding="utf-8") for name in label["evidence_files"]}
        full_rows = [{"filename": name, "content": value} for name, value in content.items()]
        full_messages = _prompt(root, config, controls[label["control_id"]], full_rows)
        full_tokens = estimate_tokens("\n".join(item["content"] for item in full_messages))
        retrieval_config = dict(config)
        retrieval_config["prompt_version"] = "eval_v2_retrieval"
        retrieval_rows = [{"filename": "retrieved excerpts (estimated)",
                           "content": "x" * (int(config["context_token_budget"]) * 4)}]
        retrieval_messages = _prompt(root, retrieval_config, controls[label["control_id"]], retrieval_rows)
        retrieval_tokens = estimate_tokens("\n".join(item["content"] for item in retrieval_messages))
        chosen_tokens = retrieval_tokens if config["context_mode"] == "retrieval" else full_tokens
        selected_estimates.append(chosen_tokens)
        largest = max(largest, chosen_tokens)
        print(f"{label['case_id']}: full prompt~{full_tokens} tokens; retrieval prompt~{retrieval_tokens} tokens; context window needed~{chosen_tokens + int(config['max_output_tokens'])}")
    total_seconds = 0.0
    if prompt_tps and gen_tps:
        total_seconds = sum(_project_seconds(tokens, int(config["max_output_tokens"]), float(prompt_tps),
                                             float(gen_tps), int(config["repeat"])) for tokens in selected_estimates)
        print(f"Projection: {total_seconds / 60:.1f} minutes ({total_seconds / 3600:.2f} hours) for {len(selected)} cases × {config['repeat']} repeats using {prompt_tps:.1f} prompt tok/s and {gen_tps:.1f} generation tok/s.")
        if total_seconds > 3600:
            print("WARNING: projected run exceeds one hour.")
    if config["num_ctx"] == "auto":
        chosen = math.ceil((largest + int(config["max_output_tokens"]) + int(config["num_ctx_auto_margin"])) / 1024) * 1024
        print(f"Auto num_ctx would choose {chosen} for this selection.")


def run_benchmark(root: Path, config: dict[str, Any]) -> Path | None:
    if config["dataset"] == "base":
        validate_dataset(root)
    else:
        validate_heavy_dataset(root)
    labels = load_labels(root, config["dataset"])
    selected = [row for row in labels if config["split"] == "all" or row["split"] == config["split"]]
    if config["dataset"] == "base":
        selected = [row for row in selected if config["tier"] in {"S", "all"}]
    elif config["tier"] != "all":
        selected = [row for row in selected if row.get("tier") == config["tier"]]
    if config.get("control"):
        control_filter = str(config["control"]).casefold()
        selected = [row for row in selected if row["control_id"].casefold() == control_filter or row["case_id"].casefold() == control_filter]
    status_filter = config.get("status")
    if status_filter:
        statuses = {part.strip() for part in (status_filter if isinstance(status_filter, list) else str(status_filter).split(",")) if part.strip()}
        selected = [row for row in selected if row["expected_status"] in statuses]
    if config.get("limit"):
        selected = selected[:int(config["limit"])]
    if not selected:
        raise ValueError("No test cases selected; check dataset, split, tier, control, and status filters.")
    controls = {path.stem: yaml.safe_load(path.read_text(encoding="utf-8"))
                for path in (root / "data" / "controls").glob("*.yaml")}
    if config.get("dry_run"):
        _dry_run(root, config, selected, controls)
        return None

    embedding = None
    index_info: dict[str, Any] = {}
    index_build_seconds = 0.0
    store_path = root / config["cache_db"]
    if config["context_mode"] == "retrieval":
        embedding = None if config["retriever"] == "bm25" else create_embedding(config)
        index_started = time.perf_counter()
        index_info = build_index(root, config["dataset"], embedding, store_path,
                                 int(config["chunk_tokens"]), int(config["overlap"]),
                                 case_ids=[row["case_id"] for row in selected])
        index_build_seconds = time.perf_counter() - index_started

    if config["num_ctx"] == "auto":
        from .chunking import estimate_tokens
        largest = 0
        for label in selected:
            evidence_root = root / "data" / ("heavy/evidence" if config["dataset"] == "heavy" else "evidence") / label["case_id"]
            evidence = {name: (evidence_root / name).read_text(encoding="utf-8") for name in label["evidence_files"]}
            rows = [{"filename": name, "content": value} for name, value in evidence.items()]
            prompt_config = dict(config)
            if config["context_mode"] == "retrieval":
                prompt_config["prompt_version"] = "eval_v2_retrieval"
                rows = [{"filename": "retrieved excerpt", "content": "x" * int(config["context_token_budget"]) * 4}]
            messages = _prompt(root, prompt_config, controls[label["control_id"]], rows)
            largest = max(largest, estimate_tokens("\n".join(item["content"] for item in messages)))
        config["num_ctx"] = max(1024, math.ceil((largest + int(config["max_output_tokens"]) + int(config["num_ctx_auto_margin"])) / 1024) * 1024)

    run_stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    slug = re.sub(r"[^A-Za-z0-9.-]+", "-", str(config["model"])).strip("-")[:32]
    if config.get("resume"):
        resume_value = Path(str(config["resume"]))
        run_dir = resume_value if resume_value.is_absolute() else root / (resume_value if str(resume_value).startswith("runs/") else Path("runs") / resume_value)
        if not run_dir.is_dir():
            raise ValueError(f"Cannot resume; run directory does not exist: {run_dir}")
        old_config = yaml.safe_load((run_dir / "config.yaml").read_text(encoding="utf-8")) or {}
        for key in ("backend", "model", "dataset", "context_mode", "prompt_version", "query_version", "tier"):
            saved_value = old_config.get(key, DEFAULTS.get(key))
            if saved_value != config.get(key):
                raise ValueError(f"Cannot resume with a different {key}: saved={saved_value!r}, requested={config.get(key)!r}")
        (run_dir / "cases").mkdir(parents=True, exist_ok=True)
    else:
        runs_dir = root / "runs"
        runs_dir.mkdir(parents=True, exist_ok=True)
        suffix = 1
        run_dir = runs_dir / f"{run_stamp}_{slug}_{config['dataset']}_{config['context_mode']}_{config['tier']}"
        while run_dir.exists():
            run_dir = runs_dir / f"{run_stamp}_{slug}_{config['dataset']}_{config['context_mode']}_{config['tier']}_{suffix}"
            suffix += 1
        (run_dir / "cases").mkdir(parents=True)
    safe_config = dict(config)
    safe_config["api_key_configured"] = bool(safe_config.pop("api_key", None))
    safe_config["embed_api_key_configured"] = bool(safe_config.pop("embed_api_key", None))
    (run_dir / "config.yaml").write_text(yaml.safe_dump(safe_config, sort_keys=False, allow_unicode=True), encoding="utf-8")

    data_digest = selected_data_hash(root, config["dataset"])
    backend = create_backend(config)
    backend_details = backend.environment_details()
    environment = environment_snapshot(root, config["backend"], config["model"], backend_details,
                                       "eval_v2_retrieval" if config["context_mode"] == "retrieval" else config["prompt_version"], data_digest)
    environment.update({"embedding_model": index_info.get("embedding_model"),
                        "embedding_dimension": index_info.get("embedding_dimension"),
                        "embedding_digest": index_info.get("embedding_digest"),
                        "embedding_quantization": index_info.get("embedding_quantization"),
                        "embedding_backend": index_info.get("embedding_backend"),
                        "chunk_tokens": config["chunk_tokens"] if config["context_mode"] == "retrieval" else None,
                        "chunk_overlap": config["overlap"] if config["context_mode"] == "retrieval" else None,
                        "retriever": config["retriever"] if config["context_mode"] == "retrieval" else None,
                        "top_k": config["top_k"] if config["context_mode"] == "retrieval" else None,
                        "context_mode": config["context_mode"], "query_version": config["query_version"],
                        "tier_set": sorted({row.get("tier", "S") for row in selected}),
                        "num_ctx": config["num_ctx"], "index_build_seconds": index_build_seconds,
                        "embedding_cache_hit_rate": index_info.get("cache_hit_rate")})
    write_json(run_dir / "environment.json", environment)

    weight_bytes = backend_details.get("model_size_bytes")
    available_ram = __import__("psutil").virtual_memory().available
    estimated_need = (int(weight_bytes) * 1.4 if weight_bytes else 0) + int(config["num_ctx"]) * 512 * 1024
    if estimated_need and available_ram < estimated_need:
        print(f"WARNING: available RAM ({available_ram / 2**30:.1f} GiB) is below the rough model+KV estimate ({estimated_need / 2**30:.1f} GiB).")
        environment["ram_warning"] = {"available_bytes": available_ram, "estimated_need_bytes": estimated_need}
        write_json(run_dir / "environment.json", environment)
    sampler = ResourceSampler(interval_seconds=1.0)
    sampler.start()
    warmup_started = time.perf_counter()
    try:
        warmup_completion = backend.warmup()
        warmup = {"wall_clock_seconds": time.perf_counter() - warmup_started,
                  "model_reported_total_seconds": _native_seconds(warmup_completion.metrics, "total_duration"),
                  "model_load_seconds": _native_seconds(warmup_completion.metrics, "load_duration"),
                  "prompt_tokens": warmup_completion.metrics.get("prompt_eval_count") or warmup_completion.metrics.get("prompt_tokens"),
                  "output_tokens": warmup_completion.metrics.get("eval_count") or warmup_completion.metrics.get("completion_tokens"),
                  "discarded": True}
    except BackendError as exc:
        (run_dir / "run_error.txt").write_text(str(exc) + "\n", encoding="utf-8")
        sampler.stop()
        raise
    except Exception:
        sampler.stop()
        raise

    existing_records: list[dict[str, Any]] = []
    result_path = run_dir / "results.jsonl"
    if config.get("resume") and result_path.is_file():
        selected_ids = {row["case_id"] for row in selected}
        for line in result_path.read_text(encoding="utf-8").splitlines():
            try:
                row = json.loads(line)
                if row.get("case_id") in selected_ids:
                    existing_records.append(row)
            except json.JSONDecodeError:
                continue
    previous_metrics: dict[str, Any] = {}
    previous_metrics_path = run_dir / "metrics.json"
    if config.get("resume") and previous_metrics_path.is_file():
        try:
            previous_metrics = json.loads(previous_metrics_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            previous_metrics = {}
    prior_elapsed = previous_metrics.get("total_run_seconds")
    if prior_elapsed is None:
        prior_elapsed = sum(float(row.get("wall_clock_elapsed_seconds") or row.get("wall_clock_total_seconds") or 0)
                            for row in existing_records)
    records_by_case: dict[str, list[dict[str, Any]]] = {}
    for row in existing_records:
        records_by_case.setdefault(str(row["case_id"]), []).append(row)
    for rows in records_by_case.values():
        rows.sort(key=lambda row: int(row.get("repetition", 0)))
    completed = {case_id for case_id, rows in records_by_case.items()
                 if len({int(row.get("repetition", 0)) for row in rows}) >= int(config["repeat"])}
    pending = [row for row in selected if row["case_id"] not in completed]
    records: list[dict[str, Any]] = list(existing_records)
    timed_start = time.perf_counter()
    stopped_for_budget = False
    try:
        with result_path.open("w", encoding="utf-8") as result_file:
            for old_row in existing_records:
                result_file.write(json.dumps(old_row, ensure_ascii=False) + "\n")
            result_file.flush()
            total_cases = len(selected)
            done_cases = len(completed & {row["case_id"] for row in selected})
            for position, label in enumerate(pending, start=1):
                if config.get("max_minutes") and time.perf_counter() - timed_start >= float(config["max_minutes"]) * 60:
                    stopped_for_budget = True
                    print("Time budget exhausted; writing the partial report.")
                    break
                evidence_root = root / "data" / ("heavy/evidence" if config["dataset"] == "heavy" else "evidence") / label["case_id"]
                original_evidence = {filename: (evidence_root / filename).read_text(encoding="utf-8") for filename in label["evidence_files"]}
                case_records: list[dict[str, Any]] = list(records_by_case.get(label["case_id"], []))
                next_repetition = max((int(row.get("repetition", 0)) for row in case_records), default=0) + 1
                for repetition in range(next_repetition, int(config["repeat"]) + 1):
                    if config.get("max_minutes") and time.perf_counter() - timed_start >= float(config["max_minutes"]) * 60:
                        stopped_for_budget = True
                        break
                    retrieval_meta: dict[str, Any] = {}
                    model_evidence = original_evidence
                    if config["context_mode"] == "retrieval":
                        control = controls[label["control_id"]]
                        query_template_path = root / "prompts" / f"{config['query_version']}.md"
                        if not query_template_path.is_file():
                            raise ValueError(f"Query template not found: {query_template_path}")
                        query = build_query(control, query_template_path.read_text(encoding="utf-8"))
                        key = index_key(root, config["dataset"], embedding.model if embedding else "lexical-only",
                                        int(config["chunk_tokens"]), int(config["overlap"]),
                                        getattr(embedding, "query_prefix", "") if embedding else "",
                                        getattr(embedding, "passage_prefix", "") if embedding else "")
                        store = IndexStore(store_path)
                        retrieved, retrieval_seconds, embedding_seconds = retrieve_case(
                            store, key, label["case_id"], query, config["retriever"], int(config["top_k"]), embedding)
                        context, tokens_sent = assemble_context(retrieved, int(config["context_token_budget"]), config["context_order"])
                        store.close()
                        model_evidence = _retrieval_evidence(context)
                        gold = label.get("gold_passages", [])
                        hit_count = sum(any(item["filename"] == passage["file"] and gold_hit(passage["text"], item["source_text"])
                                            for item in context) for passage in gold)
                        all_gold_retrieved = bool(gold) and hit_count == len(gold)
                        retrieval_meta = {"retrieved_chunks": [{"chunk_id": item.chunk.chunk_id, "file": item.chunk.file,
                                             "score": item.score, "rank": item.rank,
                                             "start_line": item.chunk.start_line, "end_line": item.chunk.end_line}
                                            for item in retrieved],
                                          "context_chunk_ids": [item["chunk_id"] for item in context],
                                          "tokens_sent": tokens_sent, "retrieval_seconds": retrieval_seconds,
                                          "embedding_seconds": embedding_seconds, "gold_passage_count": len(gold),
                                          "gold_passages_retrieved": hit_count, "all_gold_in_context": all_gold_retrieved,
                                          "failure_attribution": "n/a" if label["expected_status"] == "insufficient_evidence" else None}
                    backend.set_timeout(float(config["case_timeout"]) if config.get("case_timeout") else None)
                    case_started = time.perf_counter()
                    resource_sample_start = len(sampler.samples)
                    try:
                        record = _make_record(root, backend, config, label, controls[label["control_id"]],
                                              model_evidence, repetition, retrieval_meta, original_evidence)
                    except BackendError as exc:
                        elapsed = time.perf_counter() - case_started
                        if config.get("case_timeout") and "timed out" in str(exc).lower():
                            record = _timeout_record(label, repetition, retrieval_meta, elapsed)
                        else:
                            raise
                    finally:
                        backend.set_timeout(None)
                    case_samples = sampler.samples[resource_sample_start:]
                    ram_samples = [item.get("ram_used_bytes") for item in case_samples if item.get("ram_used_bytes") is not None]
                    vram_samples = [item.get("gpu_vram_used_mb") for item in case_samples if item.get("gpu_vram_used_mb") is not None]
                    record["resource_peak_ram_used_bytes"] = max(ram_samples) if ram_samples else None
                    record["resource_peak_gpu_vram_used_mb"] = max(vram_samples) if vram_samples else None
                    if retrieval_meta and label["expected_status"] != "insufficient_evidence":
                        retrieval_meta["failure_attribution"] = _failure_attribution(
                            label["expected_status"], bool(retrieval_meta.get("all_gold_in_context")),
                            bool(record["matches_expected"]), len(label.get("gold_passages", [])))
                        record["retrieval"] = retrieval_meta
                    records.append(record)
                    case_records.append(record)
                    result_file.write(json.dumps(record, ensure_ascii=False) + "\n")
                    result_file.flush()
                if case_records:
                    write_json(run_dir / "cases" / f"{label['case_id']}.json",
                               {"label": label, "control": controls[label["control_id"]], "repetitions": case_records})
                    (run_dir / "cases" / f"{label['case_id']}.md").write_text(_case_markdown(label, case_records, controls[label["control_id"]]), encoding="utf-8")
                    records_by_case[label["case_id"]] = case_records
                    case_done = len({int(row.get("repetition", 0)) for row in case_records}) >= int(config["repeat"])
                    if case_done:
                        done_cases += 1
                    elapsed = time.perf_counter() - timed_start
                    rate = done_cases / elapsed if elapsed > 0 else 0
                    eta = (total_cases - done_cases) / rate if rate else 0
                    state = "" if case_done else " (repetitions incomplete)"
                    print(f"[{done_cases}/{total_cases}] {label['case_id']}{state} — ETA {eta / 60:.1f} min", flush=True)
                if stopped_for_budget:
                    break
    except BackendError as exc:
        (run_dir / "run_error.txt").write_text(str(exc) + "\n", encoding="utf-8")
        raise
    finally:
        total_elapsed = time.perf_counter() - timed_start
        resource_metrics = sampler.stop()
    metrics = build_metrics(records, float(prior_elapsed) + total_elapsed, resource_metrics, warmup, data_digest,
                            "eval_v2_retrieval" if config["context_mode"] == "retrieval" else config["prompt_version"])
    finished_case_ids = {case_id for case_id, rows in records_by_case.items()
                         if len({int(row.get("repetition", 0)) for row in rows}) >= int(config["repeat"])}
    metrics["partial_run"] = stopped_for_budget or len(finished_case_ids.intersection({row["case_id"] for row in selected})) < len(selected)
    metrics["index_build_seconds"] = index_build_seconds
    metrics["embedding_cache_hit_rate"] = index_info.get("cache_hit_rate")
    metrics["dataset"] = config["dataset"]
    metrics["context_mode"] = config["context_mode"]
    metrics["query_version"] = config["query_version"]
    metrics["tier_set"] = sorted({row.get("tier", "S") for row in selected})
    metrics["retrieval_settings"] = {key: config[key] for key in ("retriever", "embed_model", "chunk_tokens", "overlap", "top_k", "context_token_budget")}
    write_json(run_dir / "metrics.json", metrics)
    (run_dir / "report.md").write_text(render_run_report(run_dir, config, environment, metrics, records, selected), encoding="utf-8")
    return run_dir
def _fmt(value: Any, digits: int = 3) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def render_run_report(run_dir: Path, config: dict[str, Any], environment: dict[str, Any],
                      metrics: dict[str, Any], records: list[dict[str, Any]],
                      selected: list[dict[str, Any]]) -> str:
    latency = metrics["latency_seconds"]
    resources = metrics["resource_metrics"]
    lines = [f"# Benchmark run: {run_dir.name}", "", f"- Backend/model: `{config['backend']}` / `{config['model']}`",
             f"- Split: `{config['split']}`; cases: {len(selected)}; repeats: {config['repeat']}",
             f"- Completion: {'partial' if metrics.get('partial_run') else 'complete'}",
             f"- Prompt: `{metrics.get('prompt_version', config['prompt_version'])}`; query template: `{config.get('query_version', 'n/a')}`; output language: `{config['output_language']}`",
             f"- Dataset SHA-256: `{metrics['dataset_hash']}`", "", "## Accuracy and output quality", "",
             "| Metric | Result |", "|---|---:|",
             f"| Verdict accuracy (invalid outputs count as wrong) | {_fmt(metrics['verdict_accuracy'] * 100 if metrics['verdict_accuracy'] is not None else None, 1)}% |",
             f"| Dangerous false reassurance | {metrics['dangerous_false_reassurance_count']} |",
             f"| Over-strict errors | {metrics['over_strict_error_count']} |",
             f"| Valid JSON before repair | {_fmt(metrics['initial_valid_json_rate'] * 100 if metrics['initial_valid_json_rate'] is not None else None, 1)}% |",
             f"| Valid JSON after repair | {_fmt(metrics['final_valid_json_rate'] * 100 if metrics['final_valid_json_rate'] is not None else None, 1)}% |",
             f"| Schema-valid before / after repair | {_fmt(metrics.get('initial_valid_schema_rate') * 100 if metrics.get('initial_valid_schema_rate') is not None else None, 1)}% / {_fmt(metrics.get('final_valid_schema_rate') * 100 if metrics.get('final_valid_schema_rate') is not None else None, 1)}% |",
             f"| Schema failures before repair | {metrics['schema_failure_count_before_retry']} |",
             f"| Repair calls | {metrics['repair_retry_count']} |",
             f"| Quote validity | {_fmt(metrics['quote_validity_rate'] * 100 if metrics['quote_validity_rate'] is not None else None, 1)}% ({metrics['valid_quotes']}/{metrics['total_quotes']}) |",
             f"| Prompt-injection resistance | {_fmt(metrics['prompt_injection_resistance_rate'] * 100 if metrics['prompt_injection_resistance_rate'] is not None else None, 1)}% ({metrics['prompt_injection_case_count']} cases) |",
             f"| Mean confidence, correct / incorrect | {_fmt(metrics['mean_confidence_correct'])} / {_fmt(metrics['mean_confidence_incorrect'])} |", "",
             "### Confusion matrix", "", "| Expected \\ Predicted | " + " | ".join(STATUSES) + " |", "|---|" + "---:|" * len(STATUSES)]
    for expected in STATUSES:
        lines.append("| " + expected + " | " + " | ".join(str(metrics["confusion_matrix"][expected][pred]) for pred in STATUSES) + " |")
    lines += ["", "### Per-class precision and recall", "", "| Status | Precision | Recall | Support |", "|---|---:|---:|---:|"]
    for status, values in metrics["per_class"].items():
        lines.append(f"| {status} | {_fmt(values['precision'], 2)} | {_fmt(values['recall'], 2)} | {values['support']} |")
    lines += ["", "### Accuracy by language", "", "| Language | Cases | Accuracy |", "|---|---:|---:|"]
    for language, values in metrics["accuracy_by_language"].items():
        lines.append(f"| {language} | {values['cases']} | {_fmt(values['accuracy'] * 100 if values['accuracy'] is not None else None, 1)}% |")
    lines += ["", "### Accuracy by tag", "", "| Tag | Cases | Accuracy |", "|---|---:|---:|"]
    for tag, values in metrics["accuracy_by_tag"].items():
        lines.append(f"| {tag} | {values['cases']} | {_fmt(values['accuracy'] * 100 if values['accuracy'] is not None else None, 1)}% |")
    lines += ["", "### Confidence calibration", "", "| Confidence bucket | Cases | Mean confidence | Accuracy |", "|---|---:|---:|---:|"]
    for bucket in metrics.get("confidence_calibration", []):
        lines.append(f"| {bucket['range']} | {bucket['count']} | {_fmt(bucket['mean_confidence'], 2)} | {_fmt(bucket['accuracy'] * 100 if bucket['accuracy'] is not None else None, 1)}% |")
    if metrics.get("confidence_warning"):
        lines.append(f"\n**Confidence warning:** {metrics['confidence_warning']}")
    lines += ["", "### Needle position accuracy (full context)", "", "| Position | Cases | Accuracy |", "|---|---:|---:|"]
    for position, values in metrics.get("accuracy_by_needle_position_full", {}).items():
        lines.append(f"| {position} | {values['cases']} | {_fmt(values['accuracy'] * 100 if values['accuracy'] is not None else None, 1)}% |")
    lines += ["", "### Scaling by tier and context mode", "", "| Tier / mode | Cases | Accuracy | Dangerous errors | Quote validity | Median / p95 latency | Prompt tokens | Prompt tok/s | Generation tok/s | Peak RAM GiB | Peak VRAM MB | 300-control hours |", "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for key, value in metrics.get("scaling_by_tier_and_context", {}).items():
        ram_gib = value.get("peak_ram_used_bytes") / (1024 ** 3) if value.get("peak_ram_used_bytes") else None
        lines.append(f"| {key} | {value['cases']} | {_fmt(value['verdict_accuracy'] * 100 if value['verdict_accuracy'] is not None else None, 1)}% | {value['dangerous_false_reassurance_count']} | {_fmt(value['quote_validity_rate'] * 100 if value['quote_validity_rate'] is not None else None, 1)}% | {_fmt(value['median_latency_seconds'])} / {_fmt(value['p95_latency_seconds'])} s | {_fmt(value['mean_prompt_tokens'], 0)} | {_fmt(value['mean_prompt_processing_tokens_per_second'], 1)} | {_fmt(value['mean_generation_tokens_per_second'], 1)} | {_fmt(ram_gib, 2)} | {_fmt(value.get('peak_gpu_vram_used_mb'), 0)} | {_fmt(value['projected_300_control_hours'], 2)} |")
    lines += ["", "### Paired heavy variants", "", "| Base case | Available tiers | Verdict changes vs S | Latency growth ratios vs S |", "|---|---|---:|---|"]
    for pair in metrics.get("paired_comparisons", []):
        growth = ", ".join(_fmt(value, 2) + "×" for value in pair.get("latency_growth_ratios_vs_S", [])) or "compare with a base S run"
        lines.append(f"| {pair['paired_with']} | {', '.join(pair.get('available_tiers', []))} | {pair.get('verdict_changes_vs_S', 'n/a')} | {growth} |")
    lines += ["", "## Performance", "", "| Metric | Result |", "|---|---:|",
              f"| Mean / median / p95 latency | {_fmt(latency['mean'])} / {_fmt(latency['median'])} / {_fmt(latency['p95'])} s |",
              f"| Min / max latency | {_fmt(latency['min'])} / {_fmt(latency['max'])} s |",
              f"| Mean prompt processing speed | {_fmt(metrics['mean_prompt_processing_tokens_per_second'], 1)} tokens/s |",
              f"| Mean generation speed | {_fmt(metrics['mean_generation_tokens_per_second'], 1)} tokens/s |",
              f"| Prompt-cache cases / uncached prompt-speed samples | {metrics.get('prefix_cached_case_count', 0)} / {metrics.get('uncached_prompt_speed_sample_count', 0)} |",
              f"| Mean phase shares: load / prompt / generation | {_fmt((metrics.get('phase_latency_shares') or {}).get('model_load') * 100 if (metrics.get('phase_latency_shares') or {}).get('model_load') is not None else None, 1)}% / {_fmt((metrics.get('phase_latency_shares') or {}).get('prompt_processing') * 100 if (metrics.get('phase_latency_shares') or {}).get('prompt_processing') is not None else None, 1)}% / {_fmt((metrics.get('phase_latency_shares') or {}).get('generation') * 100 if (metrics.get('phase_latency_shares') or {}).get('generation') is not None else None, 1)}% |",
              f"| Total timed run | {_fmt(metrics['total_run_seconds'])} s |",
              f"| Throughput | {_fmt(metrics['cases_per_minute'], 2)} case repetitions/min |",
              f"| Projected 300 controls | {_fmt(metrics['projected_300_control_hours'], 2)} hours |",
              f"| Warm-up load time (separate) | {_fmt(metrics['warmup'].get('model_load_seconds'))} s |",
              f"| Peak RAM used | {_fmt(resources.get('peak_ram_used_bytes') / (1024 ** 3) if resources.get('peak_ram_used_bytes') else None, 2)} GiB |",
              f"| Ollama server peak RSS | {_fmt(resources.get('peak_ollama_server_rss_bytes') / (1024 ** 3) if resources.get('peak_ollama_server_rss_bytes') else None, 2)} GiB |",
              f"| Ollama model-runner peak RSS | {_fmt(resources.get('peak_ollama_model_runner_rss_bytes') / (1024 ** 3) if resources.get('peak_ollama_model_runner_rss_bytes') else None, 2)} GiB |",
              f"| Mean benchmark process CPU | {_fmt(resources.get('mean_benchmark_process_cpu_percent'), 1)}% |",
              f"| Mean / peak system CPU | {_fmt(resources.get('mean_system_cpu_percent'), 1)}% / {_fmt(resources.get('peak_system_cpu_percent'), 1)}% |",
              f"| Peak GPU utilization / VRAM | {_fmt(resources.get('peak_gpu_utilization_percent'), 1)}% / {_fmt(resources.get('peak_gpu_vram_used_mb'), 0)} MB |",
              f"| Resource note | {'; '.join(resources.get('degradation_notes', [])) or 'Sampling available'} |", "",
              "## Cases needing review", "", "| Case | Expected | Predicted | Match | Truncation | Case file |", "|---|---|---|---|---|---|"]
    for row in records:
        if row.get("matches_expected") and not row.get("likely_truncated") and row.get("quote_validity", {}).get("valid") == row.get("quote_validity", {}).get("total"):
            continue
        lines.append(f"| {row['case_id']} (rep {row['repetition']}) | {row['expected_status']} | {row['status']} | {'yes' if row['matches_expected'] else 'no'} | {row['likely_truncated']} | [case](cases/{row['case_id']}.md) |")
    lines += ["", "## Environment", "", f"- OS: {environment['operating_system']}", f"- CPU: {environment['cpu_model']} ({environment['logical_cpu_cores']} logical cores)",
              f"- RAM: {environment['total_ram_gib']} GiB", f"- GPU: {', '.join(g['name'] for g in environment['gpu_devices']) if environment['gpu_devices'] else environment.get('gpu_note')}",
              f"- Backend version: {environment.get('backend_version') or 'not reported'}; model digest: {environment.get('model_digest') or 'not reported'}; quantization: {environment.get('quantization') or 'not reported'}",
              "", "Warm-up is excluded from the timed case throughput and its reported load time is shown separately. Ollama token counts and timing fields are native when available; OpenAI-compatible prompt counts may fall back to a character-based estimate if the server omits usage."]
    return "\n".join(lines) + "\n"


def compare_runs(run_dirs: list[Path], output: Path | None = None) -> Path:
    entries = []
    for run_dir in run_dirs:
        metrics = json.loads((run_dir / "metrics.json").read_text(encoding="utf-8"))
        environment = json.loads((run_dir / "environment.json").read_text(encoding="utf-8"))
        config = yaml.safe_load((run_dir / "config.yaml").read_text(encoding="utf-8")) or {}
        entries.append((run_dir, metrics, environment, config))
    hashes = {entry[1].get("dataset_hash") for entry in entries}
    prompts = {entry[1].get("prompt_version") for entry in entries}
    query_prompts = {entry[1].get("query_version") for entry in entries
                     if entry[3].get("context_mode") == "retrieval"}
    cache_policies = {entry[3].get("no_prompt_cache") for entry in entries}
    lines = ["# Benchmark comparison", ""]
    warnings = []
    if len(hashes) > 1:
        warnings.append("Runs use different dataset hashes; accuracy and performance are not directly comparable.")
    if len(prompts) > 1:
        warnings.append("Runs use different evaluation prompt versions; accuracy may not be directly comparable.")
    if len(query_prompts) > 1 or (query_prompts and None in query_prompts):
        warnings.append("Retrieval runs use different or unknown query template versions; retrieval quality may not be directly comparable.")
    if len(cache_policies) > 1:
        warnings.append("Runs used different prompt-cache policies; prompt-processing speeds may not be comparable.")
    if any(entry[1].get("prefix_cached_case_count") is None for entry in entries):
        warnings.append("Some runs predate prefix-cache detection; their prompt-processing speeds may include cached-prefix artifacts.")
    if warnings:
        lines += ["## Warnings", ""] + [f"- **Warning:** {warning}" for warning in warnings] + [""]
    lines += ["| Run / model | Dataset | Context | Tier(s) | Accuracy | Dangerous errors | Quote validity | JSON valid after retry | Median latency | P95 latency | Prompt tok/s | Generation tok/s | Peak RAM GiB | Peak VRAM MB | 300-control hours |",
              "|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for run_dir, metrics, environment, config in entries:
        resource = metrics.get("resource_metrics", {})
        latency = metrics.get("latency_seconds", {})
        ram_gib = resource.get("peak_ram_used_bytes") / (1024 ** 3) if resource.get("peak_ram_used_bytes") else None
        lines.append("| {} / `{}` | {} | {} | {} | {} | {} | {} | {} | {} s | {} s | {} | {} | {} | {} | {} |".format(
            run_dir.name, config.get("model", environment.get("model")), config.get("dataset", "base"),
            config.get("context_mode", "full"), ", ".join(metrics.get("tier_set", [config.get("tier", "S")])),
            _fmt(metrics.get("verdict_accuracy") * 100 if metrics.get("verdict_accuracy") is not None else None, 1) + "%",
            metrics.get("dangerous_false_reassurance_count", 0),
            _fmt(metrics.get("quote_validity_rate") * 100 if metrics.get("quote_validity_rate") is not None else None, 1) + "%",
            _fmt(metrics.get("final_valid_json_rate") * 100 if metrics.get("final_valid_json_rate") is not None else None, 1) + "%",
            _fmt(latency.get("median")), _fmt(latency.get("p95")),
            _fmt(metrics.get("mean_prompt_processing_tokens_per_second"), 1),
            _fmt(metrics.get("mean_generation_tokens_per_second"), 1), _fmt(ram_gib, 2),
            _fmt(resource.get("peak_gpu_vram_used_mb"), 0), _fmt(metrics.get("projected_300_control_hours"), 2)))
    lines += ["", "## Scaling by tier and context mode", "",
              "| Run / model | Tier / mode | Cases | Accuracy | Dangerous errors | Quote validity | Median / p95 latency | Prompt tokens | Prompt tok/s | Generation tok/s | Peak RAM GiB | Peak VRAM MB | 300-control hours |",
              "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for run_dir, metrics, environment, config in entries:
        for tier_mode, values in metrics.get("scaling_by_tier_and_context", {}).items():
            ram_gib = values.get("peak_ram_used_bytes") / (1024 ** 3) if values.get("peak_ram_used_bytes") else None
            lines.append(f"| {run_dir.name} / `{config.get('model', environment.get('model'))}` | {tier_mode} | {values.get('cases', 0)} | {_fmt(values.get('verdict_accuracy') * 100 if values.get('verdict_accuracy') is not None else None, 1)}% | {values.get('dangerous_false_reassurance_count', 0)} | {_fmt(values.get('quote_validity_rate') * 100 if values.get('quote_validity_rate') is not None else None, 1)}% | {_fmt(values.get('median_latency_seconds'))} / {_fmt(values.get('p95_latency_seconds'))} s | {_fmt(values.get('mean_prompt_tokens'), 0)} | {_fmt(values.get('mean_prompt_processing_tokens_per_second'), 1)} | {_fmt(values.get('mean_generation_tokens_per_second'), 1)} | {_fmt(ram_gib, 2)} | {_fmt(values.get('peak_gpu_vram_used_mb'), 0)} | {_fmt(values.get('projected_300_control_hours'), 2)} |")
    pair_records: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for run_dir, metrics, environment, config in entries:
        result_path = run_dir / "results.jsonl"
        if not result_path.exists():
            continue
        for line in result_path.read_text(encoding="utf-8").splitlines():
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            case_id = str(row.get("case_id", ""))
            tier = str(row.get("tier") or "S")
            base_id = row.get("paired_with") or (case_id if tier == "S" else None)
            if base_id:
                pair_key = (str(base_id), str(config.get("model", environment.get("model", "unknown"))),
                            str(config.get("context_mode", "full")))
                pair_records[pair_key].append({**row, "_comparison_tier": tier})
    if pair_records:
        lines += ["", "## Paired verdict and latency comparison", "",
                  "| Base case / model / mode | Tiers observed | Verdict changes vs S | Median latency growth vs S by tier |", "|---|---|---:|---|"]
        for (base_id, model_name, context_mode), rows in sorted(pair_records.items()):
            baseline_rows = [row for row in rows if row.get("_comparison_tier") == "S" and row.get("case_id") == base_id]
            baseline_by_repeat = {int(row.get("repetition", 1)): row for row in baseline_rows}
            baseline = next(iter(baseline_rows), None)
            tiers = sorted({str(row.get("_comparison_tier", "S")) for row in rows})
            if baseline:
                heavy_rows = [row for row in rows if row.get("_comparison_tier") in {"M", "L", "XL"}]
                comparisons = [(row, baseline_by_repeat.get(int(row.get("repetition", 1)), baseline)) for row in heavy_rows]
                changes = sum(row.get("status") != base_row.get("status") for row, base_row in comparisons)
                growth_by_tier: dict[str, list[float]] = defaultdict(list)
                for row, base_row in comparisons:
                    if row.get("wall_clock_total_seconds") and base_row.get("wall_clock_total_seconds"):
                        growth_by_tier[str(row["_comparison_tier"])].append(
                            float(row["wall_clock_total_seconds"]) / float(base_row["wall_clock_total_seconds"]))
                growth = ", ".join(f"{tier}: {statistics.median(values):.2f}×" for tier, values in sorted(growth_by_tier.items())) or "n/a"
            else:
                changes, growth = "base S run not included", "base S run not included"
            lines.append(f"| {base_id} / `{model_name}` / {context_mode} | {', '.join(tiers)} | {changes} | {growth} |")
    destination = output or Path.cwd() / "comparison.md"
    destination.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return destination
