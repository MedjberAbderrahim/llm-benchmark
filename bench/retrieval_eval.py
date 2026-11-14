"""Offline-LMM retrieval recall and sweep reporting."""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml

from .embeddings import EmbeddingBackend
from .retrieval import (IndexStore, assemble_context, build_index, build_queries, data_hash,
                        gold_hit, index_key, load_labels, retrieve_queries)


def _summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    gold_total = sum(row["gold_total"] for row in rows)
    hits_total = sum(row["gold_hits"] for row in rows)
    required_total = sum(row["required_gold_total"] for row in rows)
    required_hits = sum(row["required_gold_hits"] for row in rows)
    mrr_values = [row["mrr"] for row in rows if row["mrr"] is not None]
    evaluable = [row for row in rows if row["required_gold_total"] > 0]
    return {"cases": len(rows), "gold_passages": gold_total, "gold_hits": hits_total,
            "recall": hits_total / gold_total if gold_total else None,
            "required_gold_passages": required_total, "required_gold_hits": required_hits,
            "all_required_gold_in_context_rate": (sum(row["all_required_gold_in_context"] for row in evaluable) / len(evaluable)) if evaluable else None,
            "mrr": sum(mrr_values) / len(mrr_values) if mrr_values else None,
            "mean_context_tokens": sum(row["context_tokens"] for row in rows) / len(rows) if rows else None}


def evaluate_retrieval(root: Path, dataset: str, embedding: EmbeddingBackend | None, store_path: Path,
                       retriever: str = "hybrid", top_k: int = 8, chunk_tokens: int = 400,
                       overlap: int = 60, token_budget: int = 4000, limit: int | None = None,
                       sweep: bool = False, query_version: str = "query_v1",
                       use_hints: bool = False, min_files: int = 4) -> Path:
    chunk_sizes = [400] if sweep else [chunk_tokens]
    k_values = [5, 8] if sweep else [top_k]
    retrievers = ["dense", "bm25", "hybrid"] if sweep else [retriever]
    query_versions = ["query_v1", "query_v2"] if sweep else [query_version]
    hint_options = [False, True] if sweep else [use_hints]
    if any(method != "bm25" for method in retrievers) and embedding is None:
        raise ValueError("Dense and hybrid retrieval require a configured embedding backend")
    labels = load_labels(root, dataset)
    if not any(label.get("gold_passages") for label in labels):
        raise ValueError(f"Dataset '{dataset}' has no gold passages; retrieval evaluation requires labeled gold passages. Use --dataset heavy.")
    if limit:
        labels = labels[:limit]
    details: list[dict[str, Any]] = []
    summaries: list[dict[str, Any]] = []
    for size in chunk_sizes:
        current_overlap = min(overlap, size - 1) if not sweep else 60
        index_info = build_index(root, dataset, embedding, store_path, size, current_overlap,
                                 case_ids=[row["case_id"] for row in labels])
        key = index_info["index_key"]
        for method in retrievers:
            for current_query_version in query_versions:
                query_path = root / "prompts" / f"{current_query_version}.md"
                if not query_path.is_file():
                    raise ValueError(f"Query template not found: {query_path}")
                template = query_path.read_text(encoding="utf-8")
                for current_use_hints in hint_options:
                    store = IndexStore(store_path)
                    group_rows: list[dict[str, Any]] = []
                    for label in labels:
                        control = yaml.safe_load((root / "data" / "controls" / f"{label['control_id']}.yaml").read_text(encoding="utf-8"))
                        queries = build_queries(control, current_query_version, template, current_use_hints)
                        retrieved, retrieval_seconds, embed_seconds = retrieve_queries(
                            store, key, label["case_id"], queries, method, max(k_values),
                            embedding if method != "bm25" else None, min_files)
                        gold = label.get("gold_passages", [])
                        ranks: list[int | None] = []
                        required_ranks: list[int | None] = []
                        for passage in gold:
                            hit = next((item.rank for item in retrieved if item.chunk.file == passage["file"] and gold_hit(passage["text"], item.chunk.text)), None)
                            ranks.append(hit if hit is not None and hit <= max(k_values) else None)
                            if passage.get("required", True):
                                required_ranks.append(hit if hit is not None and hit <= max(k_values) else None)
                        for k in k_values:
                            selected = [item for item in retrieved if item.rank <= k]
                            context, context_tokens = assemble_context(selected, token_budget, "file")
                            hits = sum(rank is not None and rank <= k for rank in ranks)
                            required_hits = sum(rank is not None and rank <= k for rank in required_ranks)
                            required_total = len(required_ranks)
                            required_context_hits = sum(
                                any(item["filename"] == passage["file"] and
                                    gold_hit(passage["text"], item["source_text"])
                                    for item in context)
                                for passage in gold if passage.get("required", True))
                            first_hit = min((rank for rank in ranks if rank is not None and rank <= k), default=None)
                            shortfall_reasons = []
                            if len(retrieved) < k:
                                shortfall_reasons.append("fewer_indexed_chunks_than_requested")
                            if len(context) < min(k, len(retrieved)):
                                shortfall_reasons.append("token_budget")
                            row = {"case_id": label["case_id"], "tier": label.get("tier", "S"),
                                   "language": label["language"], "control_id": label["control_id"],
                                   "tags": label["tags"], "gold_total": len(gold), "gold_hits": hits,
                                   "required_gold_total": required_total, "required_gold_hits": required_hits,
                                   "required_gold_context_hits": required_context_hits,
                                   "all_required_gold_in_context": required_context_hits == required_total if required_total else None,
                                   "mrr": 1 / first_hit if first_hit else (0.0 if gold else None),
                                   "gold_ranks": ranks, "required_gold_ranks": required_ranks,
                                   "context_tokens": context_tokens, "retrieval_seconds": retrieval_seconds,
                                   "embedding_seconds": embed_seconds, "chunk_tokens": size,
                                   "overlap": current_overlap, "top_k": k, "retriever": method,
                                   "query_version": current_query_version, "use_hints": current_use_hints,
                                   "min_files": min_files, "chunks_requested": k,
                                   "chunks_returned": len(context),
                                   "shortfall_reason": shortfall_reasons or None,
                                   "embedding_model": embedding.model if embedding else "lexical-only",
                                   "cache_hit_rate": index_info.get("cache_hit_rate")}
                            group_rows.append(row)
                            details.append(row)
                    store.close()
                    for k in k_values:
                        summary = _summarize([row for row in group_rows if row["top_k"] == k])
                        summaries.append({"chunk_tokens": size, "overlap": current_overlap,
                                          "retriever": method, "query_version": current_query_version,
                                          "use_hints": current_use_hints, "min_files": min_files,
                                          "top_k": k,
                                          "embedding_model": embedding.model if embedding else "lexical-only",
                                          "cache_hit_rate": index_info.get("cache_hit_rate"), **summary})
    model_name = embedding.model if embedding else "lexical-only"
    report = root / "runs" / f"retrieval_{dataset}_{model_name.replace(':', '-')}.md"
    report.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"# Retrieval evaluation: {dataset}", "", f"- Dataset hash: `{data_hash(root, dataset)}`",
             f"- Query versions: `{query_versions}`; hints: `{hint_options}`; minimum files: `{min_files}`",
             f"- Embedding model: `{model_name}`", "- No LLM was called.", "",
             "| Chunk | Overlap | Retriever | Query | Hints | k | Cases | All required gold in context | Recall@k | MRR | Context tokens | Cache hits |",
             "|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    fmt = lambda value, digits=3: f"{value:.{digits}f}" if value is not None else "n/a"
    for row in summaries:
        rate = row.get("all_required_gold_in_context_rate")
        lines.append(f"| {row['chunk_tokens']} | {row['overlap']} | {row['retriever']} | {row['query_version']} | {row['use_hints']} | {row['top_k']} | {row['cases']} | {fmt(rate * 100 if rate is not None else None, 1)}% | {fmt(row['recall'])} | {fmt(row['mrr'])} | {fmt(row['mean_context_tokens'], 0)} | {fmt(row['cache_hit_rate'] * 100 if row.get('cache_hit_rate') is not None else None, 1)}% |")
    primary = details[-len(labels):] if details else []
    lines += ["", "## Breakdown by tier, language, control, and tag", ""]
    for field in ("tier", "language", "control_id"):
        groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in primary:
            groups[str(row[field])].append(row)
        lines += [f"### {field}", "", "| Value | Cases | All required in context | Recall@k | MRR |", "|---|---:|---:|---:|---:|"]
        for value, group in sorted(groups.items()):
            summary = _summarize(group)
            all_rate = summary["all_required_gold_in_context_rate"]
            lines.append(f"| {value} | {summary['cases']} | {fmt(all_rate * 100 if all_rate is not None else None, 1)}% | {fmt(summary['recall'])} | {fmt(summary['mrr'])} |")
    tag_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in primary:
        for tag in row["tags"]:
            tag_groups[tag].append(row)
    lines += ["### tags", "", "| Tag | Cases | All required in context | Recall@k | MRR |", "|---|---:|---:|---:|---:|"]
    for tag, group in sorted(tag_groups.items()):
        summary = _summarize(group)
        rate = summary["all_required_gold_in_context_rate"]
        lines.append(f"| {tag} | {summary['cases']} | {fmt(rate * 100 if rate is not None else None, 1)}% | {fmt(summary['recall'])} | {fmt(summary['mrr'])} |")
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    (report.with_suffix(".json")).write_text(json.dumps({"settings": {"dataset": dataset,
        "model": model_name, "query_versions": query_versions, "hints": hint_options,
        "min_files": min_files}, "results": summaries, "cases": details},
        ensure_ascii=False, indent=2), encoding="utf-8")
    return report
