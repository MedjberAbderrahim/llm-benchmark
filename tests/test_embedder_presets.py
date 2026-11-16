from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest
import httpx

from bench.embedder_comparison import compare_embedders
from bench.embedder_presets import DEFAULT_QUERY_INSTRUCTION, resolve_embedder
from bench.embeddings import EmbeddingError, HashEmbeddingBackend, OllamaEmbeddingBackend
from bench.retrieval import IndexStore, build_index, create_embedding
from bench.retrieval_eval import sanitize_model_name
from bench.chunking import chunk_text
from bench.heavy_data import generate_heavy_dataset


ROOT = Path(__file__).resolve().parents[1]


def test_preset_resolution_and_override_precedence() -> None:
    qwen = resolve_embedder("qwen3-embed-8b")
    assert qwen["embed_model"] == "qwen3-embedding:8b"
    assert qwen["query_prefix"] == f"Instruct: {DEFAULT_QUERY_INSTRUCTION}\nQuery: "
    assert qwen["passage_prefix"] == ""
    override = resolve_embedder("qwen3-embed-8b", model="custom-model",
                                query_prefix="Q: ", passage_prefix="P: ", query_instruction="custom task")
    assert override["embed_model"] == "custom-model"
    assert override["query_prefix"] == "Q: " and override["passage_prefix"] == "P: "
    assert override["query_instruction"] == "custom task"
    nemotron = resolve_embedder("nemotron-embed-8b")
    assert nemotron["query_prefix"] == "query: " and nemotron["passage_prefix"] == "passage: "
    assert resolve_embedder("bge-m3")["query_prefix"] == ""
    with pytest.raises(ValueError, match="does not support --embed-dim"):
        resolve_embedder("bge-m3", embed_dim=256)


def test_query_instruction_applies_to_query_but_not_passage() -> None:
    backend = HashEmbeddingBackend(model="fake", dimension=32,
        query_prefix="Instruct: compliance retrieval\nQuery: ", passage_prefix="")
    raw_query = HashEmbeddingBackend(model="fake", dimension=32).embed(["find policy"], "query")[0]
    instructed_query = backend.embed(["find policy"], "query")[0]
    raw_passage = backend.embed(["find policy"], "passage")[0]
    assert not np.allclose(raw_query, instructed_query)
    assert np.allclose(raw_passage, raw_query)


def test_ollama_adapter_sends_query_prefix_only_and_disables_truncation() -> None:
    requests = []

    def handler(request: httpx.Request) -> httpx.Response:
        payload = json.loads(request.content)
        requests.append(payload)
        return httpx.Response(200, json={"embeddings": [[1.0, 0.0] for _ in payload["input"]]})

    backend = OllamaEmbeddingBackend("http://ollama.invalid", "fake", query_prefix="query: ",
                                     passage_prefix="passage: ")
    backend.client.close()
    backend.client = httpx.Client(transport=httpx.MockTransport(handler))
    backend.embed(["control text"], "query")
    backend.embed(["evidence text"], "passage")
    assert requests[0]["input"] == ["query: control text"]
    assert requests[1]["input"] == ["passage: evidence text"]
    assert requests[0]["truncate"] is False
    backend.client.close()


def test_ollama_embedding_errors_distinguish_slow_from_missing_model() -> None:
    def timeout_handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("slow local inference", request=request)

    backend = OllamaEmbeddingBackend("http://ollama.invalid", "fake-model", timeout=17)
    backend.client.close()
    backend.client = httpx.Client(transport=httpx.MockTransport(timeout_handler))
    with pytest.raises(EmbeddingError, match="exceeded the 17s read timeout.*service was reachable"):
        backend.embed(["chunk"])
    backend.client.close()

    missing = OllamaEmbeddingBackend("http://ollama.invalid", "missing-model")
    missing.client.close()
    missing.client = httpx.Client(transport=httpx.MockTransport(
        lambda request: httpx.Response(404, text="model not found")))
    with pytest.raises(EmbeddingError, match="HTTP 404.*ollama pull missing-model"):
        missing.embed(["chunk"])
    missing.client.close()


def test_ollama_vector_dimension_truncation_and_normalization() -> None:
    backend = OllamaEmbeddingBackend("http://localhost:11434", "fake", embed_dim=2)
    result = backend._process([[3.0, 4.0, 100.0]])[0]
    assert len(result) == 2 and np.isclose(np.linalg.norm(result), 1.0)
    assert np.allclose(result, [0.6, 0.8])
    with pytest.raises(EmbeddingError, match="exceeds model dimension"):
        OllamaEmbeddingBackend("http://localhost:11434", "fake", embed_dim=4)._process([[1.0, 2.0, 3.0]])


def test_index_rejects_mixed_vector_dimensions(tmp_path: Path) -> None:
    store = IndexStore(tmp_path / "index.sqlite3")
    one = chunk_text("one.md", "first text", 20, 0, 1)[0]
    two = chunk_text("two.md", "second text", 20, 0, 1)[0]
    store.put_chunk("mixed", "case", one, "fake", np.array([1.0, 0.0], dtype=np.float32))
    store.put_chunk("mixed", "case", two, "fake", np.array([1.0, 0.0, 0.0], dtype=np.float32))
    store.commit()
    with pytest.raises(ValueError, match="mixed dimensions"):
        store.assert_index_dimensions("mixed")
    store.close()


def test_filename_sanitization() -> None:
    assert sanitize_model_name("maternion/nemotron:8b") == "maternion-nemotron-8b"


class _FakeComparisonEmbedding(HashEmbeddingBackend):
    def __init__(self, config: dict):
        super().__init__(model=config["embed_model"], dimension=24,
                         query_prefix=config["query_prefix"], passage_prefix=config["passage_prefix"],
                         embed_dim=config.get("embed_dim"))
        self.embedder_preset = config.get("embedder")
        self.embedding_backend = "fake"

    def details(self) -> dict:
        return {**super().details(), "embedding_backend": "fake", "embedding_digest": "fixture",
                "embedding_quantization": "none", "ollama_version": "offline-test"}


def test_comparison_report_builds_from_fake_embeddings(tmp_path: Path) -> None:
    from bench.data_generation import build_dataset

    build_dataset(tmp_path)
    generate_heavy_dataset(tmp_path, seed=11)
    (tmp_path / "prompts").mkdir(exist_ok=True)
    for name in ("query_v1.md", "query_v2.md"):
        (tmp_path / "prompts" / name).write_text((ROOT / "prompts" / name).read_text(encoding="utf-8"), encoding="utf-8")
    config = {"dataset": "heavy", "embedders": ["bge-m3"], "limit": 1,
              "chunk_tokens": 400, "overlap": 60, "top_k": [3], "min_files": 2,
              "query_version": ["query_v1"], "use_hints": False,
              "cache_db": tmp_path / ".cache" / "retrieval.sqlite3"}
    report = compare_embedders(tmp_path, config, backend_factory=_FakeComparisonEmbedding)
    payload = json.loads(report.with_suffix(".json").read_text(encoding="utf-8"))
    assert report.exists() and payload["results"]
    assert payload["cost"]["bge-m3"]["dimension"] == 24
    assert "no-hints dense-only" in report.read_text(encoding="utf-8")
