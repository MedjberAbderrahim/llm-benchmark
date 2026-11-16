"""SQLite-backed per-case dense, BM25, and reciprocal-rank retrieval."""
from __future__ import annotations

import hashlib
import json
import math
import re
import sqlite3
import time
from collections.abc import Callable
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import yaml

from .chunking import Chunk, chunk_dict, chunk_text, estimate_tokens
from .embeddings import EmbeddingBackend, OllamaEmbeddingBackend, OpenAIEmbeddingBackend
from .embedder_presets import resolve_embedder
from .heavy_data import heavy_dataset_hash
from .util import dataset_hash


def create_embedding(config: dict[str, Any]) -> EmbeddingBackend:
    resolved = resolve_embedder(config.get("embedder"), config.get("embed_model"),
                                config.get("query_prefix"), config.get("passage_prefix"),
                                config.get("query_instruction"), config.get("embed_dim"))
    config.update(resolved)
    backend = config.get("embed_backend", "ollama")
    base_url = config.get("embed_base_url") or config.get("base_url") or "http://localhost:11434"
    model = config.get("embed_model", "bge-m3")
    if backend == "ollama":
        adapter = OllamaEmbeddingBackend(base_url, model,
                                      timeout=float(config.get("embed_timeout", 1800)),
                                      query_prefix=config.get("query_prefix", ""),
                                      passage_prefix=config.get("passage_prefix", ""),
                                      embed_dim=config.get("embed_dim"))
        adapter.embedder_preset = resolved.get("embedder")
        return adapter
    if backend == "openai":
        adapter = OpenAIEmbeddingBackend(base_url, config.get("embed_api_key") or config.get("api_key"), model,
                                      timeout=float(config.get("embed_timeout", 600)),
                                      query_prefix=config.get("query_prefix", ""),
                                      passage_prefix=config.get("passage_prefix", ""),
                                      embed_dim=config.get("embed_dim"))
        adapter.embedder_preset = resolved.get("embedder")
        return adapter
    raise ValueError("embed_backend must be ollama or openai")

TOKEN_RE = re.compile(r"(?u)[\w]+(?:[./:-][\w]+)*(?:/\d+)?")


def tokenize(text: str) -> list[str]:
    return [match.group(0).casefold() for match in TOKEN_RE.finditer(text)]


def bm25_scores(query: str, documents: list[str], k1: float = 1.5, b: float = 0.75) -> list[float]:
    query_terms = tokenize(query)
    doc_terms = [tokenize(document) for document in documents]
    n = len(documents)
    if not n:
        return []
    lengths = [len(tokens) for tokens in doc_terms]
    avg_len = sum(lengths) / n or 1
    frequencies = [Counter(tokens) for tokens in doc_terms]
    df = Counter(term for terms in (set(tokens) for tokens in doc_terms) for term in terms)
    scores = []
    for terms, counts, length in zip(doc_terms, frequencies, lengths):
        score = 0.0
        for term in query_terms:
            tf = counts.get(term, 0)
            if not tf:
                continue
            idf = math.log(1 + (n - df[term] + 0.5) / (df[term] + 0.5))
            score += idf * tf * (k1 + 1) / (tf + k1 * (1 - b + b * length / avg_len))
        scores.append(score)
    return scores


def reciprocal_rank_fusion(rankings: list[list[str]], k: int = 60) -> list[tuple[str, float]]:
    scores: Counter[str] = Counter()
    for ranking in rankings:
        for rank, item in enumerate(ranking, start=1):
            scores[item] += 1.0 / (k + rank)
    return sorted(scores.items(), key=lambda pair: (-pair[1], pair[0]))


def gold_hit(gold: str, chunk: str, threshold: float = 0.8) -> bool:
    if not gold:
        return False
    if gold in chunk:
        return True
    # Compare the fraction of gold covered by the longest common contiguous span.
    from difflib import SequenceMatcher
    match = SequenceMatcher(None, gold, chunk, autojunk=False).find_longest_match(0, len(gold), 0, len(chunk))
    return match.size / len(gold) >= threshold


@dataclass
class RetrievedChunk:
    chunk: Chunk
    score: float
    rank: int
    header: str | None = None


class IndexStore:
    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(path)
        self.connection.execute("PRAGMA journal_mode=WAL")
        self.connection.executescript("""
            CREATE TABLE IF NOT EXISTS embedding_cache (
              embedding_model TEXT NOT NULL, content_hash TEXT NOT NULL,
              dimension INTEGER NOT NULL, vector BLOB NOT NULL,
              PRIMARY KEY (embedding_model, content_hash));
            CREATE TABLE IF NOT EXISTS chunks (
              index_key TEXT NOT NULL, case_id TEXT NOT NULL, chunk_id TEXT NOT NULL,
              metadata TEXT NOT NULL, content_hash TEXT NOT NULL,
              embedding_model TEXT, vector BLOB,
              PRIMARY KEY (index_key, case_id, chunk_id));
            CREATE INDEX IF NOT EXISTS chunks_by_case ON chunks(index_key, case_id);
        """)
        self.connection.commit()

    def cache_get(self, model: str, content_hash: str) -> np.ndarray | None:
        row = self.connection.execute("SELECT dimension, vector FROM embedding_cache WHERE embedding_model=? AND content_hash=?", (model, content_hash)).fetchone()
        if not row:
            return None
        vector = np.frombuffer(row[1], dtype=np.float32).copy()
        if len(vector) != int(row[0]):
            raise ValueError(f"Cached embedding dimension mismatch for model cache key {model!r}: stored={row[0]}, vector={len(vector)}")
        return vector

    def cache_put(self, model: str, content_hash: str, vector: np.ndarray) -> None:
        vector = np.asarray(vector, dtype=np.float32)
        self.connection.execute("INSERT OR IGNORE INTO embedding_cache VALUES (?, ?, ?, ?)", (model, content_hash, len(vector), vector.tobytes()))

    def clear_index(self, index_key: str, case_ids: list[str] | None = None) -> None:
        if case_ids is None:
            self.connection.execute("DELETE FROM chunks WHERE index_key=?", (index_key,))
        else:
            self.connection.executemany("DELETE FROM chunks WHERE index_key=? AND case_id=?",
                                        [(index_key, case_id) for case_id in case_ids])

    def put_chunk(self, index_key: str, case_id: str, chunk: Chunk, model: str | None, vector: np.ndarray | None) -> None:
        content_hash = hashlib.sha256(chunk.text.encode("utf-8")).hexdigest()
        metadata = chunk_dict(chunk)
        self.connection.execute("INSERT OR REPLACE INTO chunks VALUES (?, ?, ?, ?, ?, ?, ?)",
                                (index_key, case_id, chunk.chunk_id, json.dumps(metadata, ensure_ascii=False), content_hash,
                                 model, vector.astype(np.float32).tobytes() if vector is not None else None))

    def get_case_chunks(self, index_key: str, case_id: str) -> list[tuple[Chunk, np.ndarray | None]]:
        rows = self.connection.execute("SELECT metadata, vector FROM chunks WHERE index_key=? AND case_id=? ORDER BY json_extract(metadata, '$.start_char')", (index_key, case_id)).fetchall()
        result = []
        for raw, vector_blob in rows:
            item = json.loads(raw)
            chunk = Chunk(item["chunk_id"], item["file"], item["text"], item["start_char"], item["end_char"],
                          item["start_line"], item["end_line"], tuple(item["heading_path"]), item.get("header"))
            vector = np.frombuffer(vector_blob, dtype=np.float32).copy() if vector_blob else None
            result.append((chunk, vector))
        return result

    def commit(self) -> None:
        self.connection.commit()

    def close(self) -> None:
        self.connection.close()

    def assert_index_dimensions(self, index_key: str) -> int | None:
        rows = self.connection.execute("SELECT DISTINCT length(vector) FROM chunks WHERE index_key=? AND vector IS NOT NULL", (index_key,)).fetchall()
        dimensions = {int(row[0]) // 4 for row in rows if row[0] is not None}
        if len(dimensions) > 1:
            raise ValueError(f"Index {index_key} contains vectors with mixed dimensions: {sorted(dimensions)}")
        return next(iter(dimensions)) if dimensions else None

    def index_bytes(self, index_key: str) -> int:
        row = self.connection.execute("SELECT COALESCE(SUM(length(metadata)+COALESCE(length(vector),0)),0) FROM chunks WHERE index_key=?", (index_key,)).fetchone()
        return int(row[0] or 0)


def load_labels(root: Path, dataset: str) -> list[dict[str, Any]]:
    name = "labels_heavy.yaml" if dataset == "heavy" else "labels.yaml"
    return yaml.safe_load((root / "data" / name).read_text(encoding="utf-8"))


def data_paths(root: Path, dataset: str, label: dict[str, Any]) -> tuple[Path, Path]:
    evidence_root = root / "data" / ("heavy/evidence" if dataset == "heavy" else "evidence") / label["case_id"]
    return evidence_root, root / "data" / "controls" / f"{label['control_id']}.yaml"


def data_hash(root: Path, dataset: str) -> str:
    return heavy_dataset_hash(root) if dataset == "heavy" else dataset_hash(root)


def index_key(root: Path, dataset: str, model: str, chunk_tokens: int, overlap: int,
              query_prefix: str = "", passage_prefix: str = "", embed_dim: int | None = None,
              model_digest: str | None = None, backend: str | None = None) -> str:
    raw = f"{data_hash(root, dataset)}:{backend}:{model}:{model_digest}:{chunk_tokens}:{overlap}:{query_prefix}:{passage_prefix}:{embed_dim}"
    return hashlib.sha256(raw.encode()).hexdigest()


def build_index(root: Path, dataset: str, embedding: EmbeddingBackend | None, store_path: Path,
                chunk_tokens: int = 400, overlap: int = 60, batch_size: int = 4,
                case_ids: list[str] | None = None,
                progress: Callable[[int, int], None] | None = None) -> dict[str, Any]:
    if dataset not in {"base", "heavy"}:
        raise ValueError("dataset must be base or heavy")
    if batch_size < 1:
        raise ValueError("embed_batch_size must be positive")
    labels = load_labels(root, dataset)
    model_name = embedding.model if embedding is not None else "lexical-only"
    initial_details = embedding.details() if embedding is not None else {}
    model_digest = initial_details.get("embedding_digest")
    key = index_key(root, dataset, model_name, chunk_tokens, overlap,
                    getattr(embedding, "query_prefix", "") if embedding else "",
                    getattr(embedding, "passage_prefix", "") if embedding else "",
                    getattr(embedding, "embed_dim", None) if embedding else None,
                    model_digest, initial_details.get("embedding_backend"))
    store = IndexStore(store_path)
    labels = [row for row in labels if case_ids is None or row["case_id"] in set(case_ids)]
    store.clear_index(key, [row["case_id"] for row in labels])
    chunks_by_case: list[tuple[str, Chunk]] = []
    for label in labels:
        evidence_root, _ = data_paths(root, dataset, label)
        for filename in label["evidence_files"]:
            content = (evidence_root / filename).read_text(encoding="utf-8")
            chunks_by_case.extend((label["case_id"], chunk) for chunk in chunk_text(filename, content, chunk_tokens, overlap))
    embedded: dict[tuple[str, str], np.ndarray] = {}
    misses: list[tuple[str, str, str]] = []
    hits = 0
    passage_prefix = getattr(embedding, "passage_prefix", "") if embedding is not None else ""
    cache_model = f"{initial_details.get('embedding_backend')}|{embedding.model}|digest={model_digest}|dim={getattr(embedding, 'embed_dim', None)}" if embedding else ""
    if embedding is not None:
        for case_id, chunk in chunks_by_case:
            content_hash = hashlib.sha256((passage_prefix + chunk.text).encode("utf-8")).hexdigest()
            cached = store.cache_get(cache_model, content_hash)
            if cached is not None:
                embedded[(case_id, chunk.chunk_id)] = cached
                hits += 1
            else:
                # Adapters apply their configured passage prefix themselves.
                misses.append((case_id, chunk.chunk_id, chunk.text))
    by_key = {(case_id, chunk.chunk_id): chunk for case_id, chunk in chunks_by_case}
    if embedding is not None:
        for start in range(0, len(misses), batch_size):
            batch = misses[start:start + batch_size]
            vectors = embedding.embed([entry[2] for entry in batch], "passage")
            for (case_id, chunk_id, text), vector in zip(batch, vectors):
                vector = np.asarray(vector, dtype=np.float32)
                embedded[(case_id, chunk_id)] = vector
                store.cache_put(cache_model, hashlib.sha256((passage_prefix + text).encode("utf-8")).hexdigest(), vector)
            if progress is not None:
                progress(min(start + len(batch), len(misses)), len(misses))
    for case_id, chunk in chunks_by_case:
        vector = embedded.get((case_id, chunk.chunk_id))
        store.put_chunk(key, case_id, chunk, model_name if embedding is not None else None, vector)
    store.commit()
    details = initial_details if embedding is not None else {"embedding_backend": None, "embedding_model": None, "embedding_dimension": None}
    vectors = list(embedded.values())
    dimensions = {len(vector) for vector in vectors}
    if len(dimensions) > 1:
        raise ValueError(f"Index build returned mixed embedding dimensions for {model_name}: {sorted(dimensions)}")
    details["embedding_dimension"] = next(iter(dimensions)) if dimensions else getattr(embedding, "dimension", None)
    details["embedding_requested_dimension"] = getattr(embedding, "embed_dim", None) if embedding else None
    indexed_dimension = store.assert_index_dimensions(key)
    if details["embedding_dimension"] is not None and indexed_dimension not in {None, details["embedding_dimension"]}:
        raise ValueError(f"Index dimension assertion failed: vectors={indexed_dimension}, backend={details['embedding_dimension']}")
    details["embedding_dimension"] = indexed_dimension or details.get("embedding_dimension")
    details["embedding_preset"] = getattr(embedding, "embedder_preset", None) if embedding else None
    details["index_size_bytes"] = store.index_bytes(key)
    result = {"index_key": key, "dataset": dataset, "dataset_hash": data_hash(root, dataset),
              "embedding_model": embedding.model if embedding is not None else None,
              "chunk_tokens": chunk_tokens, "overlap_tokens": overlap,
              "chunk_count": len(chunks_by_case), "case_count": len(labels), "cache_hits": hits,
              "cache_misses": len(misses), "cache_hit_rate": hits / len(chunks_by_case) if chunks_by_case else None,
              **details}
    store.close()
    return result


def build_query(control: dict[str, Any], template: str | None = None) -> str:
    criteria = "\n".join(f"- {item}" for item in control.get("evaluation_criteria", []))
    expected = "\n".join(f"- {item}" for item in control.get("expected_evidence", []))
    if template is not None:
        values = {"{{TITLE}}": str(control.get("title", "")),
                  "{{DESCRIPTION}}": str(control.get("description", "")),
                  "{{EVALUATION_CRITERIA}}": criteria,
                  "{{EXPECTED_EVIDENCE}}": expected}
        query = template
        for marker, value in values.items():
            query = query.replace(marker, value)
        if re.search(r"\{\{[A-Z_]+\}\}", query):
            raise ValueError("Query template contains an unsupported placeholder")
        return query.strip()
    parts = [control.get("title", ""), control.get("description", ""),
             "Evaluation criteria:", *control.get("evaluation_criteria", []),
             "Expected evidence:", *control.get("expected_evidence", [])]
    return "\n".join(str(part) for part in parts if part)


def build_queries(control: dict[str, Any], query_version: str = "query_v1",
                  template: str | None = None, use_hints: bool = False) -> list[str]:
    """Create one legacy query or a combined + per-criterion query set."""
    hints = control.get("retrieval_hints", []) if use_hints else []
    hint_text = "\n".join(str(value) for value in hints)
    combined = build_query(control, template)
    if query_version == "query_v1":
        return [combined + (f"\nRetrieval concepts and key aliases:\n{hint_text}" if hint_text else "")]
    if query_version != "query_v2":
        raise ValueError("query_version must be query_v1 or query_v2")
    queries = [combined + (f"\nRetrieval concepts and key aliases:\n{hint_text}" if hint_text else "")]
    for criterion in control.get("evaluation_criteria", []):
        query = f"{control.get('title', '')}\n{criterion}"
        if hint_text:
            query += f"\nRetrieval concepts and key aliases:\n{hint_text}"
        queries.append(query)
    return queries


def _diversify(ranked: list[tuple[str, float]], by_id: dict[str, Chunk],
               top_k: int, min_files: int) -> list[tuple[str, float]]:
    if min_files <= 1 or not ranked:
        return ranked[:top_k]
    first_by_file: list[tuple[str, float]] = []
    seen_files: set[str] = set()
    for chunk_id, score in ranked:
        filename = by_id[chunk_id].file
        if filename not in seen_files:
            first_by_file.append((chunk_id, score))
            seen_files.add(filename)
            if len(first_by_file) >= min_files:
                break
    selected_ids = {chunk_id for chunk_id, _ in first_by_file}
    diversified = first_by_file + [(cid, score) for cid, score in ranked if cid not in selected_ids]
    return diversified[:top_k]


def retrieve_case(store: IndexStore, index_key_value: str, case_id: str, query: str,
                  retriever: str = "hybrid", top_k: int = 8, embedding: EmbeddingBackend | None = None,
                  rrf_k: int = 60, min_files: int = 4) -> tuple[list[RetrievedChunk], float, float]:
    started = time.perf_counter()
    rows = store.get_case_chunks(index_key_value, case_id)
    retrieval_read_elapsed = time.perf_counter() - started
    if not rows:
        return [], retrieval_read_elapsed, 0.0
    docs = [chunk.text + ("\n" + chunk.header if chunk.header else "") for chunk, _ in rows]
    bm25 = bm25_scores(query, docs)
    # Include zero-score rows as deterministic backfill candidates. Previously
    # those rows were discarded, so BM25 often returned fewer than top_k.
    bm25_rank = [rows[i][0].chunk_id for i in sorted(range(len(bm25)),
                                                      key=lambda i: (-bm25[i], rows[i][0].chunk_id))]
    dense_rank: list[str] = []
    dense_scores: dict[str, float] = {}
    embed_elapsed = 0.0
    if retriever in {"dense", "hybrid"}:
        if embedding is None:
            raise ValueError("Dense retrieval requires an embedding backend")
        embed_start = time.perf_counter()
        query_vector = embedding.embed([query], "query")[0]
        embed_elapsed = time.perf_counter() - embed_start
        for (chunk, vector) in rows:
            if vector is not None:
                score = float(np.dot(query_vector, vector))
                dense_scores[chunk.chunk_id] = score
        dense_rank = sorted(dense_scores, key=lambda chunk_id: (-dense_scores[chunk_id], chunk_id))
    if retriever == "bm25":
        score_by_id = {chunk.chunk_id: bm25[index] for index, (chunk, _) in enumerate(rows)}
        ranking = [(chunk_id, score_by_id[chunk_id]) for chunk_id in bm25_rank]
    elif retriever == "dense":
        ranking = [(chunk_id, dense_scores[chunk_id]) for chunk_id in dense_rank]
    elif retriever == "hybrid":
        fused = reciprocal_rank_fusion([dense_rank, bm25_rank], rrf_k)
        ranking = fused
    else:
        raise ValueError("retriever must be dense, bm25, or hybrid")
    by_id = {chunk.chunk_id: chunk for chunk, _ in rows}
    ranking = _diversify(ranking, by_id, top_k, min_files)
    retrieved = [RetrievedChunk(by_id[cid], float(score), rank) for rank, (cid, score) in enumerate(ranking, start=1)]
    return retrieved, max(0.0, time.perf_counter() - started - embed_elapsed), embed_elapsed


def retrieve_queries(store: IndexStore, index_key_value: str, case_id: str, queries: list[str],
                     retriever: str = "hybrid", top_k: int = 8,
                     embedding: EmbeddingBackend | None = None, min_files: int = 4,
                     rrf_k: int = 60) -> tuple[list[RetrievedChunk], float, float]:
    if len(queries) <= 1:
        query = queries[0] if queries else ""
        return retrieve_case(store, index_key_value, case_id, query, retriever, top_k,
                             embedding, rrf_k, min_files)
    started = time.perf_counter()
    rankings: list[list[str]] = []
    per_query: dict[str, RetrievedChunk] = {}
    retrieval_elapsed = embedding_elapsed = 0.0
    for query in queries:
        rows, retrieval_seconds, embed_seconds = retrieve_case(
            store, index_key_value, case_id, query, retriever, top_k, embedding,
            rrf_k, min_files=1)
        retrieval_elapsed += retrieval_seconds
        embedding_elapsed += embed_seconds
        rankings.append([item.chunk.chunk_id for item in rows])
        per_query.update({item.chunk.chunk_id: item for item in rows})
    fused = reciprocal_rank_fusion(rankings, rrf_k)
    by_id = {item.chunk.chunk_id: item.chunk for item in per_query.values()}
    fused_scored = [(chunk_id, score) for chunk_id, score in fused]
    fused_scored = _diversify(fused_scored, by_id, top_k, min_files)
    result = [RetrievedChunk(by_id[cid], score, rank) for rank, (cid, score) in enumerate(fused_scored, 1)]
    elapsed = max(retrieval_elapsed, time.perf_counter() - started - embedding_elapsed)
    return result, elapsed, embedding_elapsed


def assemble_context(results: list[RetrievedChunk], token_budget: int = 4000,
                     order: str = "file") -> tuple[list[dict[str, Any]], int]:
    if order not in {"file", "score"}:
        raise ValueError("context order must be file or score")
    ranked = sorted(results, key=lambda row: (row.chunk.file, row.chunk.start_char)) if order == "file" else results
    context: list[dict[str, Any]] = []
    used = 0
    for item in ranked:
        chunk = item.chunk
        content = chunk.text
        if chunk.header:
            content = f"CSV header (metadata): {chunk.header}\n{content}"
        cost = estimate_tokens(content)
        if context and used + cost > token_budget:
            continue
        if not context and cost > token_budget:
            # Keep a prefix only if the budget is smaller than the first chunk. Mark it
            # as context text; quote checks still target the original source.
            char_cap = max(1, token_budget * 4)
            content = content[:char_cap]
            cost = estimate_tokens(content)
        used += cost
        context.append({"filename": chunk.file, "content": content,
                        "start_line": chunk.start_line, "end_line": chunk.end_line,
                        "heading_path": list(chunk.heading_path), "start_char": chunk.start_char,
                        "end_char": chunk.end_char, "chunk_id": chunk.chunk_id,
                        "score": item.score, "rank": item.rank, "source_text": chunk.text,
                        "header": chunk.header})
    return context, used
