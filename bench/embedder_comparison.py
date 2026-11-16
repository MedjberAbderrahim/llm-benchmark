"""Side-by-side retrieval and cost comparison for configured embedders."""
from __future__ import annotations

import json
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import yaml

from .embedder_presets import resolve_embedder
from .embeddings import check_embedding_context
from .resources import ResourceSampler
from .retrieval import (IndexStore, build_index, build_queries, create_embedding, data_hash,
                        load_labels)
from .retrieval_eval import evaluate_retrieval


def _percentile(values: list[float], p: float) -> float | None:
    if not values:
        return None
    vals = sorted(values)
    return vals[min(len(vals) - 1, max(0, round((len(vals) - 1) * p)))]


def _query_latency(root: Path, labels: list[dict[str, Any]], embedding: Any,
                   query_version: str, use_hints: bool) -> list[float]:
    template_path = root / "prompts" / f"{query_version}.md"
    template = template_path.read_text(encoding="utf-8")
    elapsed: list[float] = []
    for label in labels:
        control = yaml.safe_load((root / "data/controls" / f"{label['control_id']}.yaml").read_text(encoding="utf-8"))
        for query in build_queries(control, query_version, template, use_hints):
            started = time.perf_counter()
            embedding.embed([query], "query")
            elapsed.append(time.perf_counter() - started)
    return elapsed


def compare_embedders(root: Path, config: dict[str, Any],
                      backend_factory: Callable[[dict[str, Any]], Any] | None = None) -> Path:
    """Run identical retrieval evaluations and emit a reproducible combined report."""
    dataset = config.get("dataset", "heavy")
    labels = load_labels(root, dataset)
    if not any(label.get("gold_passages") for label in labels):
        raise ValueError(f"Dataset '{dataset}' has no gold passages; embedder comparison requires gold labels.")
    if config.get("limit"):
        labels = labels[:int(config["limit"])]
    cache_path = Path(config.get("cache_db") or ".cache/retrieval.sqlite3")
    if not cache_path.is_absolute():
        cache_path = root / cache_path
    top_ks = list(config.get("top_k") or [5, 8])
    versions = list(config.get("query_version") or ["query_v1", "query_v2"])
    hint_modes = [bool(config.get("use_hints", False))]
    embedders = list(config.get("embedders") or ["bge-m3", "qwen3-embed-8b", "nemotron-embed-8b"])
    rows: list[dict[str, Any]] = []
    observations: list[dict[str, Any]] = []
    cost: dict[str, dict[str, Any]] = {}

    # Lexical baseline is embedder-independent and is evaluated exactly once.
    baseline_path = evaluate_retrieval(root, dataset, None, cache_path, "bm25", max(top_ks),
        int(config.get("chunk_tokens", 400)), int(config.get("overlap", 60)), limit=len(labels),
        query_version=versions[0], use_hints=hint_modes[0], min_files=int(config.get("min_files", 4)), top_k_values=top_ks)
    baseline = json.loads(baseline_path.with_suffix(".json").read_text(encoding="utf-8"))
    for result in baseline["results"]:
        if result["retriever"] == "bm25":
            rows.append({**result, "embedder": "BM25 reference", "embedder_preset": None})

    for preset_name in embedders:
        resolved = resolve_embedder(preset_name, config.get("embed_model"), config.get("query_prefix"),
                                    config.get("passage_prefix"), config.get("query_instruction"),
                                    config.get("embed_dim"))
        resolved.update({key: config.get(key) for key in (
            "embed_backend", "embed_base_url", "embed_api_key", "embed_timeout", "embed_batch_size")})
        resolved["embedder"] = preset_name
        embedding = (backend_factory(resolved) if backend_factory else create_embedding(resolved))
        print(f"Checking embedding model {embedding.model!r}; the first request may load it into memory...", flush=True)
        check_embedding_context(embedding, int(config.get("chunk_tokens", 400)))
        sampler = ResourceSampler(interval_seconds=0.5)
        sampler.start()
        started = time.perf_counter()
        try:
            index_info = build_index(root, dataset, embedding, cache_path,
                int(config.get("chunk_tokens", 400)), int(config.get("overlap", 60)),
                batch_size=int(config.get("embed_batch_size", 4)),
                case_ids=[item["case_id"] for item in labels],
                progress=lambda done, total: print(f"\rEmbedding chunks: {done}/{total}", end="", flush=True))
            print()
            index_seconds = time.perf_counter() - started
            query_times_by_mode = {(version, hints): _query_latency(root, labels, embedding, version, hints)
                                   for version in versions for hints in hint_modes}
            for version in versions:
                for hints in hint_modes:
                    query_times = query_times_by_mode[(version, hints)]
                    for method in ("dense", "hybrid"):
                        report_path = evaluate_retrieval(root, dataset, embedding, cache_path, method,
                            max(top_ks), int(config.get("chunk_tokens", 400)), int(config.get("overlap", 60)),
                            limit=len(labels), query_version=version, use_hints=hints,
                            min_files=int(config.get("min_files", 4)), top_k_values=top_ks,
                            embed_batch_size=int(config.get("embed_batch_size", 4)))
                        evaluation = json.loads(report_path.with_suffix(".json").read_text(encoding="utf-8"))
                        observations.extend({**case, "embedder": preset_name} for case in evaluation.get("cases", [])
                                            if case.get("retriever") == method and case.get("query_version") == version and case.get("use_hints") == hints)
                        for result in evaluation["results"]:
                            if result["retriever"] != method or result["top_k"] not in top_ks or result["query_version"] != version or result["use_hints"] != hints:
                                continue
                            rows.append({**result, "embedder": preset_name, "embedder_preset": preset_name,
                                "query_latency_median_seconds": statistics.median(query_times) if query_times else None,
                                "query_latency_p95_seconds": _percentile(query_times, .95),
                                "index_seconds": index_seconds,
                                "chunks_per_second": index_info["chunk_count"] / index_seconds if index_seconds else None,
                                "chunk_count": index_info["chunk_count"],
                                "dimension": index_info.get("embedding_dimension"),
                                "index_mb": index_info.get("index_size_bytes", 0) / (1024 * 1024),
                                "embedding_details": {key: index_info.get(key) for key in (
                                    "embedding_model", "embedding_digest", "embedding_quantization",
                                    "embedding_dimension", "embedding_raw_dimension", "embedding_requested_dimension",
                                    "query_prefix", "passage_prefix", "ollama_version")}})
            resource = sampler.stop()
            for row in rows:
                if row.get("embedder") == preset_name:
                    row["peak_runner_rss_bytes"] = resource.get("peak_benchmark_process_rss_bytes")
                    row["peak_gpu_vram_mb"] = resource.get("peak_gpu_vram_used_mb")
            cost[preset_name] = {"index_seconds": index_seconds, "chunk_count": index_info["chunk_count"],
                "chunks_per_second": index_info["chunk_count"] / index_seconds if index_seconds else None,
                "dimension": index_info.get("embedding_dimension"),
                "index_mb": index_info.get("index_size_bytes", 0) / (1024 * 1024),
                "query_latency_by_mode": {f"{version}|hints={hints}": {
                    "median_seconds": statistics.median(samples) if samples else None,
                    "p95_seconds": _percentile(samples, .95), "query_count": len(samples)}
                    for (version, hints), samples in query_times_by_mode.items()},
                "query_latency_median_seconds": (statistics.median(next(iter(query_times_by_mode.values())))
                    if query_times_by_mode and next(iter(query_times_by_mode.values())) else None),
                "query_latency_p95_seconds": (_percentile(next(iter(query_times_by_mode.values())), .95)
                    if query_times_by_mode else None),
                "peak_ram_bytes": resource.get("peak_ram_used_bytes"),
                "peak_runner_rss_bytes": resource.get("peak_benchmark_process_rss_bytes"),
                "peak_gpu_vram_mb": resource.get("peak_gpu_vram_used_mb"),
                "details": embedding.details()}
        finally:
            try:
                sampler.stop()
            except Exception:
                pass
            unload = getattr(embedding, "unload", None)
            if callable(unload):
                unload()

    # Annotate language/tier and hard-case slices from case-level rows.
    out = root / "runs"
    out.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    json_path = out / f"embedder_comparison_{stamp}.json"
    md_path = json_path.with_suffix(".md")
    slices: list[dict[str, Any]] = []
    label_by_id = {item["case_id"]: item for item in labels}
    for item in observations:
        label = label_by_id.get(item["case_id"], {})
        passages = label.get("gold_passages", [])
        hard_type = "config excerpt" if any(Path(gold.get("file", "")).suffix.lower() in {".yaml", ".yml", ".json", ".ini", ".conf", ".csv", ".log"} for gold in passages) else "policy prose"
        item["hard_type"] = hard_type
    group_fields = ("language", "tier", "hard_type")
    for dimension in group_fields:
        for key in sorted({(item.get("embedder"), item.get("retriever"), item.get("query_version"), item.get("use_hints"), item.get("top_k"), str(item.get(dimension, "unknown"))) for item in observations}):
            selected = [item for item in observations if (item.get("embedder"), item.get("retriever"), item.get("query_version"), item.get("use_hints"), item.get("top_k"), str(item.get(dimension, "unknown"))) == key]
            gold_total = sum(item.get("gold_total", 0) for item in selected)
            evaluable = [item for item in selected if item.get("required_gold_total", 0) > 0]
            slices.append({"embedder": key[0], "retriever": key[1], "query_version": key[2], "use_hints": key[3], "top_k": key[4],
                "slice": dimension, "value": key[5], "cases": len(selected),
                "required_evidence_recall": sum(bool(item.get("all_required_gold_in_context")) for item in evaluable) / len(evaluable) if evaluable else None,
                "recall": sum(item.get("gold_hits", 0) for item in selected) / gold_total if gold_total else None,
                "mrr": sum(item.get("mrr") or 0 for item in selected) / len(selected) if selected else None,
                "ndcg": sum(item.get("ndcg") or 0 for item in selected) / len(selected) if selected else None,
                "hit_at_1": sum(bool(item.get("hit_at_1")) for item in selected) / len(selected) if selected else None,
                "hit_at_k": sum(bool(item.get("hit_at_k")) for item in selected) / len(selected) if selected else None})
    payload = {"dataset": dataset, "dataset_hash": data_hash(root, dataset),
        "chunk_tokens": int(config.get("chunk_tokens", 400)), "overlap": int(config.get("overlap", 60)),
        "top_k": top_ks, "min_files": int(config.get("min_files", 4)), "embedders": embedders,
        "settings": {"query_versions": versions, "use_hints": hint_modes}, "cost": cost, "results": rows, "slices": slices}
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    fields = ("retriever", "embedder", "query_version", "use_hints", "top_k", "all_required_gold_in_context_rate", "recall", "mrr", "ndcg", "hit_at_1", "hit_at_k", "mean_context_tokens", "index_seconds", "chunks_per_second", "query_latency_median_seconds", "query_latency_p95_seconds", "dimension", "index_mb", "peak_runner_rss_bytes", "peak_gpu_vram_mb")
    lines = ["# Embedder comparison", "", f"- Dataset: `{dataset}`; hash: `{payload['dataset_hash']}`",
        f"- Chunk settings: `{payload['chunk_tokens']}` tokens, overlap `{payload['overlap']}`; k={top_ks}; min-files={payload['min_files']}",
        f"- Presets and prefixes: `{json.dumps({name: cost.get(name, {}).get('details', {}) for name in embedders}, ensure_ascii=False)}`", "",
        "## Results", "", "| " + " | ".join(fields) + " |", "|" + "|".join(["---"] * len(fields)) + "|"]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(field, "")) for field in fields) + " |")
    lines += ["", "## Slices", "", "| Embedder | Retriever | Query | Hints | k | Slice | Value | Cases | Required recall | Recall | MRR | nDCG | hit@1 | hit@k |", "|---|---|---|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---:|"]
    for item in slices:
        lines.append("| " + " | ".join(str(item.get(field, "")) for field in ("embedder", "retriever", "query_version", "use_hints", "top_k", "slice", "value", "cases", "required_evidence_recall", "recall", "mrr", "ndcg", "hit_at_1", "hit_at_k")) + " |")
    lines += ["",
        "## How to read this", "", "Compare dense-only with hints disabled to isolate embedding quality. Hybrid and hinted query_v2 results describe the complete retrieval pipeline and may benefit from lexical hints.", "",
        "## Limitations", "", f"Synthetic evidence only ({len(labels)} cases). Hints and query_v2 may flatter lexical retrieval. The no-hints dense-only column is the fairest measure of the embedder itself. Resource sampling is local to the runner machine; remote server GPU memory is not observable."]
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return md_path
