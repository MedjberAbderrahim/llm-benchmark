"""Offline-LMM retrieval recall and sweep reporting."""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml

from .embeddings import EmbeddingBackend
from .retrieval import (IndexStore, assemble_context, build_index, build_query, data_hash,
                        gold_hit, index_key, load_labels, retrieve_case)


def _summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    gold_total = sum(row["gold_total"] for row in rows)
    hits_total = sum(row["gold_hits"] for row in rows)
    mrr_values = [row["mrr"] for row in rows if row["mrr"] is not None]
    return {"cases": len(rows), "gold_passages": gold_total, "gold_hits": hits_total,
            "recall": hits_total / gold_total if gold_total else None,
            "mrr": sum(mrr_values) / len(mrr_values) if mrr_values else None,
            "mean_context_tokens": sum(row["context_tokens"] for row in rows) / len(rows) if rows else None}


def evaluate_retrieval(root: Path, dataset: str, embedding: EmbeddingBackend | None, store_path: Path,
                       retriever: str = "hybrid", top_k: int = 8, chunk_tokens: int = 400,
                       overlap: int = 60, token_budget: int = 4000, limit: int | None = None,
                       sweep: bool = False, query_version: str = "query_v1") -> Path:
    chunk_sizes = [200, 400, 800] if sweep else [chunk_tokens]
    k_values = [3, 5, 8, 12] if sweep else [top_k]
    retrievers = ["dense", "bm25", "hybrid"] if sweep else [retriever]
    if any(method != "bm25" for method in retrievers) and embedding is None:
        raise ValueError("Dense and hybrid retrieval require a configured embedding backend")
    labels = load_labels(root, dataset)
    query_path = root / "prompts" / f"{query_version}.md"
    if not query_path.is_file():
        raise ValueError(f"Query template not found: {query_path}")
    query_template = query_path.read_text(encoding="utf-8")
    if limit:
        labels = labels[:limit]
    results = []
    detail_rows = []
    for size in chunk_sizes:
        current_overlap = min(overlap, size - 1) if not sweep else min(60, size // 6)
        index_info = build_index(root, dataset, embedding, store_path, size, current_overlap)
        key = index_info["index_key"]
        for method in retrievers:
            store = IndexStore(store_path)
            for label in labels:
                control = yaml.safe_load((root / "data" / "controls" / f"{label['control_id']}.yaml").read_text(encoding="utf-8"))
                query = build_query(control, query_template)
                retrieved, retrieval_seconds, embed_seconds = retrieve_case(store, key, label["case_id"], query,
                                                                              method, max(k_values), embedding if method != "bm25" else None)
                gold_passages = label.get("gold_passages", [])
                context, context_tokens = assemble_context(retrieved, token_budget, "file")
                context_tokens_by_k = {k: assemble_context(retrieved[:k], token_budget, "file")[1] for k in k_values}
                hit_ranks: list[int] = []
                for gold in gold_passages:
                    hit = next((item.rank for item in retrieved if item.chunk.file == gold["file"] and gold_hit(gold["text"], item.chunk.text)), None)
                    if hit is not None and hit <= max(k_values):
                        hit_ranks.append(hit)
                gold_hits = len(hit_ranks)
                row = {"case_id": label["case_id"], "tier": label.get("tier", "S"), "language": label["language"],
                       "control_id": label["control_id"], "tags": label["tags"], "gold_total": len(gold_passages),
                       "gold_hits": gold_hits, "mrr": (1 / min(hit_ranks)) if hit_ranks else (0.0 if gold_passages else None),
                       "gold_ranks": hit_ranks,
                       "context_tokens": context_tokens, "retrieval_seconds": retrieval_seconds,
                       "embedding_seconds": embed_seconds, "chunk_tokens": size, "overlap": current_overlap,
                       "context_tokens_by_k": context_tokens_by_k,
                       "top_k": max(k_values), "retriever": method}
                detail_rows.append(row)
            store.close()
            for k in k_values:
                sub = []
                for row in detail_rows:
                    if row["chunk_tokens"] == size and row["retriever"] == method:
                        ranks = [rank for rank in row["gold_ranks"] if rank <= k]
                        sub.append({**row, "gold_hits": len(ranks),
                                    "mrr": 1 / min(ranks) if ranks else (0.0 if row["gold_total"] else None),
                                    "context_tokens": row["context_tokens_by_k"][k]})
                summary = _summarize(sub)
                results.append({"chunk_tokens": size, "overlap": current_overlap, "top_k": k,
                                "retriever": method, **summary,
                                "embedding_model": embedding.model if embedding else "lexical-only",
                                "cache_hit_rate": index_info["cache_hit_rate"]})
    model_name = embedding.model if embedding else "lexical-only"
    report = root / "runs" / f"retrieval_{dataset}_{model_name.replace(':', '-')}.md"
    report.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"# Retrieval evaluation: {dataset}", "", f"- Dataset hash: `{data_hash(root, dataset)}`",
             f"- Query template: `{query_version}`",
             f"- Embedding model: `{model_name}`", "- No LLM was called.", "",
             "| Chunk | Overlap | Retriever | k | Gold passages | Hits | Recall@k | MRR | Mean context tokens | Cache hit rate |",
             "|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|"]
    for row in results:
        fmt = lambda value, digits=3: f"{value:.{digits}f}" if value is not None else "n/a"
        lines.append(f"| {row['chunk_tokens']} | {row['overlap']} | {row['retriever']} | {row['top_k']} | {row['gold_passages']} | {row['gold_hits']} | {fmt(row['recall'])} | {fmt(row['mrr'])} | {fmt(row['mean_context_tokens'], 0)} | {fmt(row['cache_hit_rate'] * 100 if row['cache_hit_rate'] is not None else None, 1)}% |")
    primary_size = chunk_sizes[-1]
    primary_method = "hybrid" if sweep else retriever
    primary_rows = [row for row in detail_rows if row["chunk_tokens"] == primary_size and row["retriever"] == primary_method]
    lines += ["", f"## Breakdown by tier, language, control, and tag (chunk {primary_size}, {primary_method})", ""]
    for field in ("tier", "language", "control_id"):
        groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in primary_rows:
            groups[str(row[field])].append(row)
        lines += [f"### {field}", "", "| Value | Cases | Recall | MRR | Mean context tokens |", "|---|---:|---:|---:|---:|"]
        for value, group in sorted(groups.items()):
            summary = _summarize(group)
            lines.append(f"| {value} | {summary['cases']} | {summary['recall'] if summary['recall'] is not None else 0:.3f} | {summary['mrr'] if summary['mrr'] is not None else 0:.3f} | {summary['mean_context_tokens'] or 0:.0f} |")
        lines.append("")
    tag_rows: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in primary_rows:
        for tag in row["tags"]:
            tag_rows[tag].append(row)
    lines += ["### tags", "", "| Tag | Cases | Recall | MRR |", "|---|---:|---:|---:|"]
    for tag, group in sorted(tag_rows.items()):
        summary = _summarize(group)
        lines.append(f"| {tag} | {summary['cases']} | {summary['recall'] or 0:.3f} | {summary['mrr'] or 0:.3f} |")
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    (report.with_suffix(".json")).write_text(json.dumps({"settings": {"dataset": dataset, "model": model_name},
                                                            "results": results, "cases": detail_rows}, ensure_ascii=False, indent=2), encoding="utf-8")
    return report
