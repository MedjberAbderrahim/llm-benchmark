from __future__ import annotations

import math
import statistics
from collections import defaultdict
from typing import Any

STATUSES = ["compliant", "partial", "non_compliant", "insufficient_evidence"]


def percentile(values: list[float], quantile: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    pos = (len(ordered) - 1) * quantile
    low, high = math.floor(pos), math.ceil(pos)
    return ordered[low] if low == high else ordered[low] + (ordered[high] - ordered[low]) * (pos - low)


def _accuracy_breakdown(records: list[dict[str, Any]], field: str, values: set[str] | None = None) -> dict[str, Any]:
    buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in records:
        value = row.get(field)
        if isinstance(value, list):
            for item in value:
                buckets[str(item)].append(row)
        elif value is not None:
            buckets[str(value)].append(row)
    for value in values or set():
        buckets.setdefault(value, [])
    return {key: {"cases": len(rows), "correct": sum(bool(row.get("matches_expected")) for row in rows),
                  "accuracy": sum(bool(row.get("matches_expected")) for row in rows) / len(rows) if rows else None}
            for key, rows in sorted(buckets.items())}


def _calibration(scored: list[dict[str, Any]]) -> dict[str, Any]:
    intervals = [(0, .2), (.2, .4), (.4, .6), (.6, .8), (.8, 1.000001)]
    buckets = []
    for low, high in intervals:
        rows = [r for r in scored if r.get("confidence") is not None and low <= float(r["confidence"]) < high]
        buckets.append({"range": f"{low:.1f}-{min(high, 1):.1f}", "count": len(rows),
                        "mean_confidence": statistics.mean(float(r["confidence"]) for r in rows) if rows else None,
                        "accuracy": sum(bool(r.get("matches_expected")) for r in rows) / len(rows) if rows else None})
    correct = [float(r["confidence"]) for r in scored if r.get("matches_expected") and r.get("confidence") is not None]
    wrong = [float(r["confidence"]) for r in scored if not r.get("matches_expected") and r.get("confidence") is not None]
    mean_correct = statistics.mean(correct) if correct else None
    mean_wrong = statistics.mean(wrong) if wrong else None
    warning = None
    if mean_correct is not None and mean_wrong is not None and abs(mean_correct - mean_wrong) < .05:
        warning = "Mean confidence differs by less than 0.05 between correct and incorrect verdicts; confidence did not separate outcomes in this run."
    return {"buckets": buckets, "mean_correct": mean_correct, "mean_incorrect": mean_wrong, "warning": warning}


def _group_metrics(rows: list[dict[str, Any]], total_seconds: float | None = None) -> dict[str, Any]:
    latencies = [float(r["wall_clock_total_seconds"]) for r in rows if r.get("wall_clock_total_seconds") is not None]
    quotes = [q for r in rows for q in r.get("quotes", [])]
    prompt_rates = [float(r["prompt_processing_tokens_per_second"]) for r in rows
                    if r.get("prompt_processing_tokens_per_second") is not None and not r.get("prefix_cached")]
    generation_rates = [float(r["generation_tokens_per_second"]) for r in rows if r.get("generation_tokens_per_second") is not None]
    prompt_tokens = [int(r.get("prompt_tokens") or 0) for r in rows]
    cpm = len(rows) / (total_seconds / 60) if total_seconds and total_seconds > 0 else None
    ram = [int(r["resource_peak_ram_used_bytes"]) for r in rows if r.get("resource_peak_ram_used_bytes") is not None]
    vram = [float(r["resource_peak_gpu_vram_used_mb"]) for r in rows if r.get("resource_peak_gpu_vram_used_mb") is not None]
    confidences = [float(r["confidence"]) for r in rows if r.get("confidence") is not None]
    return {"cases": len(rows), "verdict_accuracy": sum(bool(r.get("matches_expected")) for r in rows) / len(rows) if rows else None,
            "dangerous_false_reassurance_count": sum(r.get("status") == "compliant" and r.get("expected_status") in {"partial", "non_compliant"} for r in rows),
            "quote_validity_rate": sum(bool(q.get("valid")) for q in quotes) / len(quotes) if quotes else None,
            "median_latency_seconds": statistics.median(latencies) if latencies else None,
            "p95_latency_seconds": percentile(latencies, .95),
            "mean_prompt_tokens": statistics.mean(prompt_tokens) if prompt_tokens else None,
            "mean_prompt_processing_tokens_per_second": statistics.mean(prompt_rates) if prompt_rates else None,
            "mean_generation_tokens_per_second": statistics.mean(generation_rates) if generation_rates else None,
            "cases_per_minute": cpm, "projected_300_control_hours": 300 / cpm / 60 if cpm else None,
            "peak_ram_used_bytes": max(ram) if ram else None, "peak_gpu_vram_used_mb": max(vram) if vram else None,
            "mean_confidence": statistics.mean(confidences) if confidences else None}


def build_metrics(records: list[dict[str, Any]], total_run_seconds: float, resource_metrics: dict[str, Any],
                  warmup: dict[str, Any], dataset_hash: str, prompt_version: str) -> dict[str, Any]:
    scored = [r for r in records if r.get("status") in STATUSES]
    matrix = {actual: {pred: 0 for pred in STATUSES} for actual in STATUSES}
    for row in records:
        if row.get("expected_status") in matrix and row.get("status") in STATUSES:
            matrix[row["expected_status"]][row["status"]] += 1
    per_class = {}
    for status in STATUSES:
        tp = matrix[status][status]
        predicted = sum(matrix[actual][status] for actual in STATUSES)
        support = sum(r.get("expected_status") == status for r in records)
        per_class[status] = {"precision": tp / predicted if predicted else None,
                             "recall": tp / support if support else None, "support": support}
    dangerous = sum(r.get("status") == "compliant" and r.get("expected_status") in {"partial", "non_compliant"} for r in records)
    over_strict = sum((r.get("expected_status") == "compliant" and r.get("status") in {"partial", "non_compliant"}) or
                      (r.get("expected_status") == "partial" and r.get("status") == "non_compliant") for r in records)
    quotes = [q for r in records for q in r.get("quotes", [])]
    if quotes:
        quote_valid_count, quote_total = sum(bool(q.get("valid")) for q in quotes), len(quotes)
    else:
        quote_valid_count = sum(int(r.get("quote_validity", {}).get("valid", 0)) for r in records)
        quote_total = sum(int(r.get("quote_validity", {}).get("total", 0)) for r in records)
    initial = sum(bool(r.get("initial_json_valid", r.get("initial_schema_valid"))) for r in records)
    final = sum(bool(r.get("final_json_valid", r.get("final_schema_valid"))) for r in records)
    initial_schema = sum(bool(r.get("initial_schema_valid")) for r in records)
    final_schema = sum(bool(r.get("final_schema_valid")) for r in records)
    injections = [r for r in records if "injection" in r.get("tags", [])]
    confidence = _calibration(scored)
    latencies = [float(r["wall_clock_total_seconds"]) for r in records if r.get("wall_clock_total_seconds") is not None]
    prompt_rates = [float(r["prompt_processing_tokens_per_second"]) for r in records
                    if r.get("prompt_processing_tokens_per_second") is not None and not r.get("prefix_cached")]
    generation_rates = [float(r["generation_tokens_per_second"]) for r in records if r.get("generation_tokens_per_second") is not None]
    cpm = len(records) / (total_run_seconds / 60) if total_run_seconds > 0 else None
    phase_sets = [r.get("phase_latency_shares", {}) for r in records]
    phase_shares = {phase: statistics.mean([float(p[phase]) for p in phase_sets if p.get(phase) is not None])
                    if any(p.get(phase) is not None for p in phase_sets) else None
                    for phase in ("model_load", "prompt_processing", "generation")}
    scaling = {}
    for tier in sorted({str(r.get("tier", "S")) for r in records}):
        for mode in sorted({str(r.get("context_mode", "full")) for r in records if str(r.get("tier", "S")) == tier}):
            group = [r for r in records if str(r.get("tier", "S")) == tier and str(r.get("context_mode", "full")) == mode]
            scaling[f"{tier}:{mode}"] = _group_metrics(group, sum(float(r.get("wall_clock_total_seconds") or 0) for r in group))
    needle = [r for r in records if r.get("context_mode", "full") == "full" and r.get("needle_position") in {"start", "middle", "end"}]
    pairs: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in records:
        if row.get("paired_with"):
            pairs[str(row["paired_with"])].append(row)
    pair_rows = []
    for base_id, group in sorted(pairs.items()):
        baseline = next((r for r in group if str(r.get("tier")) == "S"), None)
        pair_rows.append({"paired_with": base_id, "available_tiers": sorted({str(r.get("tier")) for r in group}),
                          "verdict_changes_vs_S": sum(r.get("status") != baseline.get("status") for r in group) if baseline else None,
                          "latency_growth_ratios_vs_S": [float(r["wall_clock_total_seconds"]) / float(baseline["wall_clock_total_seconds"])
                              for r in group if baseline and baseline.get("wall_clock_total_seconds") and r.get("wall_clock_total_seconds")]})
    return {
        "selected_case_repetitions": len(records), "scored_outputs": len(scored),
        "verdict_accuracy": sum(bool(r.get("matches_expected")) for r in records) / len(records) if records else None,
        "confusion_matrix": matrix, "per_class": per_class,
        "dangerous_false_reassurance_count": dangerous, "over_strict_error_count": over_strict,
        "initial_valid_json_schema_count": initial_schema, "initial_valid_json_rate": initial / len(records) if records else None,
        "final_valid_json_schema_count": final_schema, "final_valid_json_rate": final / len(records) if records else None,
        "initial_valid_schema_rate": initial_schema / len(records) if records else None,
        "final_valid_schema_rate": final_schema / len(records) if records else None,
        "schema_failure_count_before_retry": sum(not r.get("initial_schema_valid", False) for r in records),
        "final_invalid_output_count": sum(r.get("status") == "invalid_output" for r in records),
        "repair_retry_count": sum(int(r.get("retry_count", 0)) for r in records),
        "quote_validity_rate": quote_valid_count / quote_total if quote_total else None,
        "valid_quotes": quote_valid_count, "total_quotes": quote_total,
        "prompt_injection_case_count": len(injections),
        "prompt_injection_resistance_rate": sum(bool(r.get("matches_expected")) for r in injections) / len(injections) if injections else None,
        "accuracy_by_tag": _accuracy_breakdown(records, "tags"),
        "accuracy_by_language": _accuracy_breakdown(records, "language", {"en", "fr", "mixed"}),
        "mean_confidence_correct": confidence["mean_correct"], "mean_confidence_incorrect": confidence["mean_incorrect"],
        "confidence_calibration": confidence["buckets"], "confidence_warning": confidence["warning"],
        "latency_seconds": {"mean": statistics.mean(latencies) if latencies else None,
                            "median": statistics.median(latencies) if latencies else None,
                            "p95": percentile(latencies, .95), "min": min(latencies) if latencies else None,
                            "max": max(latencies) if latencies else None},
        "mean_prompt_processing_tokens_per_second": statistics.mean(prompt_rates) if prompt_rates else None,
        "mean_generation_tokens_per_second": statistics.mean(generation_rates) if generation_rates else None,
        "prefix_cached_case_count": sum(bool(r.get("prefix_cached")) for r in records),
        "uncached_prompt_speed_sample_count": len(prompt_rates), "phase_latency_shares": phase_shares,
        "prompt_token_latency_relation": {"mean_prompt_tokens": statistics.mean([float(r.get("prompt_tokens") or 0) for r in records]) if records else None,
                                           "mean_latency_seconds": statistics.mean(latencies) if latencies else None},
        "accuracy_by_needle_position_full": _accuracy_breakdown(needle, "needle_position", {"start", "middle", "end"}),
        "scaling_by_tier_and_context": scaling, "paired_comparisons": pair_rows,
        "total_run_seconds": total_run_seconds, "cases_per_minute": cpm,
        "projected_300_control_minutes": 300 / cpm if cpm else None,
        "projected_300_control_hours": 300 / cpm / 60 if cpm else None,
        "resource_metrics": resource_metrics, "warmup": warmup, "dataset_hash": dataset_hash,
        "prompt_version": prompt_version,
    }
