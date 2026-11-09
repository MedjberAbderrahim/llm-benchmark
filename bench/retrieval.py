"""SQLite-backed per-case dense, BM25, and reciprocal-rank retrieval."""
from __future__ import annotations

import hashlib
import json
import math
import re
import sqlite3
import time
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import yaml

from .chunking import Chunk, chunk_dict, chunk_text, estimate_tokens
from .embeddings import EmbeddingBackend, OllamaEmbeddingBackend, OpenAIEmbeddingBackend
from .heavy_data import heavy_dataset_hash
from .util import dataset_hash


def create_embedding(config: dict[str, Any]) -> EmbeddingBackend:
    backend = config.get("embed_backend", "ollama")
    base_url = config.get("embed_base_url") or config.get("base_url") or "http://localhost:11434"
    model = config.get("embed_model", "bge-m3")
    if backend == "ollama":
        return OllamaEmbeddingBackend(base_url, model,
                                      query_prefix=config.get("query_prefix", ""),
                                      passage_prefix=config.get("passage_prefix", ""))
    if backend == "openai":
        return OpenAIEmbeddingBackend(base_url, config.get("embed_api_key") or config.get("api_key"), model,
                                      query_prefix=config.get("query_prefix", ""),
                                      passage_prefix=config.get("passage_prefix", ""))
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
        return np.frombuffer(row[1], dtype=np.float32).copy() if row else None

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


def load_labels(root: Path, dataset: str) -> list[dict[str, Any]]:
    name = "labels_heavy.yaml" if dataset == "heavy" else "labels.yaml"
    return yaml.safe_load((root / "data" / name).read_text(encoding="utf-8"))


def data_paths(root: Path, dataset: str, label: dict[str, Any]) -> tuple[Path, Path]:
    evidence_root = root / "data" / ("heavy/evidence" if dataset == "heavy" else "evidence") / label["case_id"]
    return evidence_root, root / "data" / "controls" / f"{label['control_id']}.yaml"


def data_hash(root: Path, dataset: str) -> str:
    return heavy_dataset_hash(root) if dataset == "heavy" else dataset_hash(root)


def index_key(root: Path, dataset: str, model: str, chunk_tokens: int, overlap: int,
              query_prefix: str = "", passage_prefix: str = "") -> str:
    raw = f"{data_hash(root, dataset)}:{model}:{chunk_tokens}:{overlap}:{query_prefix}:{passage_prefix}"
    return hashlib.sha256(raw.encode()).hexdigest()


def build_index(root: Path, dataset: str, embedding: EmbeddingBackend | None, store_path: Path,
                chunk_tokens: int = 400, overlap: int = 60, batch_size: int = 32,
                case_ids: list[str] | None = None) -> dict[str, Any]:
    if dataset not in {"base", "heavy"}:
        raise ValueError("dataset must be base or heavy")
    labels = load_labels(root, dataset)
    model_name = embedding.model if embedding is not None else "lexical-only"
    key = index_key(root, dataset, model_name, chunk_tokens, overlap,
                    getattr(embedding, "query_prefix", "") if embedding else "",
                    getattr(embedding, "passage_prefix", "") if embedding else "")
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
    if embedding is not None:
        for case_id, chunk in chunks_by_case:
            content_hash = hashlib.sha256((passage_prefix + chunk.text).encode("utf-8")).hexdigest()
            cached = store.cache_get(embedding.model, content_hash)
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
                store.cache_put(embedding.model, hashlib.sha256((passage_prefix + text).encode("utf-8")).hexdigest(), vector)
    for case_id, chunk in chunks_by_case:
        vector = embedded.get((case_id, chunk.chunk_id))
        store.put_chunk(key, case_id, chunk, model_name if embedding is not None else None, vector)
    store.commit()
    details = embedding.details() if embedding is not None else {"embedding_backend": None, "embedding_model": None, "embedding_dimension": None}
    vectors = list(embedded.values())
    details["embedding_dimension"] = len(vectors[0]) if vectors else None
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


def retrieve_case(store: IndexStore, index_key_value: str, case_id: str, query: str,
                  retriever: str = "hybrid", top_k: int = 8, embedding: EmbeddingBackend | None = None,
                  rrf_k: int = 60) -> tuple[list[RetrievedChunk], float, float]:
    started = time.perf_counter()
    rows = store.get_case_chunks(index_key_value, case_id)
    retrieval_read_elapsed = time.perf_counter() - started
    if not rows:
        return [], retrieval_read_elapsed, 0.0
    docs = [chunk.text + ("\n" + chunk.header if chunk.header else "") for chunk, _ in rows]
    bm25 = bm25_scores(query, docs)
    bm25_rank = [rows[i][0].chunk_id for i in sorted((i for i, score in enumerate(bm25) if score > 0),
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
        ranking = [(chunk_id, score_by_id[chunk_id]) for chunk_id in bm25_rank[:top_k]]
    elif retriever == "dense":
        ranking = [(chunk_id, dense_scores[chunk_id]) for chunk_id in dense_rank[:top_k]]
    elif retriever == "hybrid":
        fused = reciprocal_rank_fusion([dense_rank, bm25_rank], rrf_k)
        ranking = fused[:top_k]
    else:
        raise ValueError("retriever must be dense, bm25, or hybrid")
    by_id = {chunk.chunk_id: chunk for chunk, _ in rows}
    retrieved = [RetrievedChunk(by_id[cid], float(score), rank) for rank, (cid, score) in enumerate(ranking, start=1)]
    return retrieved, max(0.0, time.perf_counter() - started - embed_elapsed), embed_elapsed


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
