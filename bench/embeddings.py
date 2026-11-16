"""Local/self-hosted embedding adapters and deterministic test backend."""
from __future__ import annotations

import hashlib
import math
import warnings
from typing import Any, Protocol

import httpx
import numpy as np


class EmbeddingError(RuntimeError):
    pass


def list_installed_ollama_models(base_url: str = "http://localhost:11434") -> tuple[set[str], str | None]:
    """Return installed Ollama model names, or a user-readable connection error."""
    try:
        response = httpx.get(base_url.rstrip("/") + "/api/tags", timeout=5)
        response.raise_for_status()
        payload = response.json()
        names: set[str] = set()
        for item in payload.get("models", []):
            for key in ("name", "model"):
                if item.get(key):
                    name = str(item[key])
                    names.add(name)
                    if name.endswith(":latest"):
                        names.add(name[:-len(":latest")])
        return names, None
    except (httpx.HTTPError, ValueError) as exc:
        return set(), str(exc)


class EmbeddingBackend(Protocol):
    model: str
    def embed(self, texts: list[str], input_type: str = "passage") -> list[np.ndarray]: ...
    def details(self) -> dict[str, Any]: ...


class OllamaEmbeddingBackend:
    def __init__(self, base_url: str, model: str, timeout: float = 1800, query_prefix: str = "", passage_prefix: str = "",
                 embed_dim: int | None = None):
        self.base_url, self.model = base_url.rstrip("/"), model
        self.query_prefix, self.passage_prefix = query_prefix, passage_prefix
        self.embed_dim = embed_dim
        self.timeout = float(timeout)
        self.client = httpx.Client(timeout=timeout)
        self.dimension: int | None = None
        self.raw_dimension: int | None = None
        self.ollama_version: str | None = None

    def embed(self, texts: list[str], input_type: str = "passage") -> list[np.ndarray]:
        prefix = self.query_prefix if input_type == "query" else self.passage_prefix
        try:
            response = self.client.post(f"{self.base_url}/api/embed", json={
                "model": self.model, "input": [prefix + text for text in texts],
                "truncate": False, "keep_alive": "5m"})
            response.raise_for_status()
            payload = response.json()
        except httpx.TimeoutException as exc:
            raise EmbeddingError(
                f"Ollama embedding request for {self.model!r} at {self.base_url} exceeded "
                f"the {self.timeout:g}s read timeout. Ollama may still be loading or "
                "processing this batch. Increase --embed-timeout, reduce --limit/chunk size, or "
                "use a smaller --embed-batch-size. The service was reachable; this is not evidence "
                "that the model is missing."
            ) from exc
        except httpx.HTTPStatusError as exc:
            body = exc.response.text[:500]
            advice = (f" Pull it with `ollama pull {self.model}`." if exc.response.status_code == 404 else "")
            raise EmbeddingError(
                f"Ollama /api/embed returned HTTP {exc.response.status_code} at {self.base_url}: "
                f"{body or exc}. Check that this Ollama version supports /api/embed and that each "
                f"input fits the embedding model context.{advice}"
            ) from exc
        except (httpx.HTTPError, ValueError) as exc:
            raise EmbeddingError(f"Could not reach Ollama embeddings at {self.base_url}: {exc}") from exc
        vectors = payload.get("embeddings")
        if not isinstance(vectors, list) or len(vectors) != len(texts):
            raise EmbeddingError("Ollama returned an unexpected embedding batch")
        return self._process(vectors)

    def _process(self, vectors: list[list[float]]) -> list[np.ndarray]:
        raw = [np.asarray(vector, dtype=np.float32) for vector in vectors]
        if raw:
            dimensions = {len(vector) for vector in raw}
            if len(dimensions) != 1:
                raise EmbeddingError(f"Embedding batch returned mixed dimensions: {sorted(dimensions)}")
            self.raw_dimension = len(raw[0])
            if self.embed_dim is not None and self.embed_dim > self.raw_dimension:
                raise EmbeddingError(f"Requested embedding dimension {self.embed_dim} exceeds model dimension {self.raw_dimension}")
        processed = [_normalize(vector[:self.embed_dim] if self.embed_dim else vector) for vector in raw]
        if processed:
            dimensions = {len(vector) for vector in processed}
            if len(dimensions) != 1:
                raise EmbeddingError("Embedding batch returned mixed dimensions after dimension reduction")
            self.dimension = len(processed[0])
        return processed

    def details(self) -> dict[str, Any]:
        details: dict[str, Any] = {"embedding_backend": "ollama", "embedding_model": self.model,
                                   "embedding_dimension": self.dimension, "embedding_raw_dimension": self.raw_dimension,
                                   "embedding_requested_dimension": self.embed_dim, "embedding_digest": None,
                                   "embedding_quantization": None,
                                   "query_prefix": self.query_prefix, "passage_prefix": self.passage_prefix,
                                   "embedding_context_length": None, "ollama_version": None}
        try:
            models = self.client.get(f"{self.base_url}/api/tags", timeout=5).json().get("models", [])
            for item in models:
                model_name = str(item.get("name") or item.get("model") or "")
                if model_name.removesuffix(":latest") == self.model.removesuffix(":latest"):
                    details["embedding_digest"] = item.get("digest")
                    details["embedding_quantization"] = (item.get("details") or {}).get("quantization_level")
                    break
        except (httpx.HTTPError, ValueError):
            pass
        try:
            shown = self.client.post(f"{self.base_url}/api/show", json={"model": self.model}, timeout=8).json()
            lengths = [value for key, value in (shown.get("model_info") or {}).items()
                       if key.endswith("context_length") and isinstance(value, int)]
            details["embedding_context_length"] = max(lengths) if lengths else None
        except (httpx.HTTPError, ValueError):
            pass
        try:
            version = self.client.get(f"{self.base_url}/api/version", timeout=5).json()
            self.ollama_version = version.get("version")
            details["ollama_version"] = self.ollama_version
        except (httpx.HTTPError, ValueError):
            pass
        return details

    def unload(self) -> None:
        try:
            response = self.client.post(f"{self.base_url}/api/generate",
                                        json={"model": self.model, "prompt": "", "stream": False,
                                              "keep_alive": 0}, timeout=15)
            response.raise_for_status()
        except (httpx.HTTPError, ValueError) as exc:
            raise EmbeddingError(f"Could not unload Ollama embedding model {self.model}: {exc}") from exc


class OpenAIEmbeddingBackend:
    def __init__(self, base_url: str, api_key: str | None, model: str, timeout: float = 300,
                 query_prefix: str = "", passage_prefix: str = "", embed_dim: int | None = None):
        normalized = base_url.rstrip("/")
        self.base_url = normalized if normalized.endswith("/v1") else normalized + "/v1"
        self.model = model
        self.query_prefix, self.passage_prefix = query_prefix, passage_prefix
        self.embed_dim = embed_dim
        headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
        self.client = httpx.Client(timeout=timeout, headers=headers)
        self.dimension: int | None = None
        self.raw_dimension: int | None = None

    def embed(self, texts: list[str], input_type: str = "passage") -> list[np.ndarray]:
        prefix = self.query_prefix if input_type == "query" else self.passage_prefix
        try:
            response = self.client.post(f"{self.base_url}/embeddings",
                                        json={"model": self.model, "input": [prefix + text for text in texts]})
            response.raise_for_status()
            data = response.json().get("data", [])
        except (httpx.HTTPError, ValueError) as exc:
            raise EmbeddingError(f"OpenAI-compatible embeddings failed at {self.base_url}: {exc}") from exc
        data.sort(key=lambda item: item.get("index", 0))
        if len(data) != len(texts):
            raise EmbeddingError("Embedding server returned an unexpected batch size")
        raw = [np.asarray(item["embedding"], dtype=np.float32) for item in data]
        dimensions = {len(vector) for vector in raw}
        if len(dimensions) > 1:
            raise EmbeddingError(f"Embedding batch returned mixed dimensions: {sorted(dimensions)}")
        self.raw_dimension = len(raw[0]) if raw else None
        if self.raw_dimension is not None and self.embed_dim is not None and self.embed_dim > self.raw_dimension:
            raise EmbeddingError(f"Requested embedding dimension {self.embed_dim} exceeds model dimension {self.raw_dimension}")
        result = [_normalize(vector[:self.embed_dim] if self.embed_dim else vector) for vector in raw]
        self.dimension = len(result[0]) if result else self.dimension
        return result

    def details(self) -> dict[str, Any]:
        return {"embedding_backend": "openai", "embedding_model": self.model, "embedding_dimension": self.dimension,
                "embedding_digest": None, "embedding_quantization": None,
                "embedding_raw_dimension": self.raw_dimension, "embedding_requested_dimension": self.embed_dim,
                "query_prefix": self.query_prefix, "passage_prefix": self.passage_prefix,
                "ollama_version": None}


class HashEmbeddingBackend:
    """Deterministic offline embedding fake for tests; not semantically meaningful."""
    def __init__(self, model: str = "fake-hash", dimension: int = 64, query_prefix: str = "",
                 passage_prefix: str = "", embed_dim: int | None = None):
        self.model, self.dimension = model, dimension
        self.query_prefix, self.passage_prefix = query_prefix, passage_prefix
        self.embed_dim = embed_dim
        self.raw_dimension = dimension

    def embed(self, texts: list[str], input_type: str = "passage") -> list[np.ndarray]:
        vectors = []
        if self.embed_dim is not None and self.embed_dim > self.raw_dimension:
            raise EmbeddingError(f"Requested embedding dimension {self.embed_dim} exceeds model dimension {self.raw_dimension}")
        for text in texts:
            vector = np.zeros(self.dimension, dtype=np.float32)
            prefix = self.query_prefix if input_type == "query" else self.passage_prefix
            for token in (prefix + text).lower().split():
                digest = hashlib.sha256(token.encode()).digest()
                index = int.from_bytes(digest[:4], "little") % self.dimension
                vector[index] += 1 if digest[4] & 1 else -1
            vectors.append(_normalize(vector[:self.embed_dim] if self.embed_dim else vector))
        if vectors:
            self.dimension = len(vectors[0])
        return vectors

    def details(self) -> dict[str, Any]:
        return {"embedding_backend": "fake", "embedding_model": self.model, "embedding_dimension": self.dimension,
                "embedding_raw_dimension": self.raw_dimension, "embedding_requested_dimension": self.embed_dim,
                "query_prefix": self.query_prefix, "passage_prefix": self.passage_prefix}


def _normalize(vector: np.ndarray) -> np.ndarray:
    norm = float(np.linalg.norm(vector))
    if norm:
        vector = vector / norm
    return vector.astype(np.float32)


def check_embedding_context(backend: EmbeddingBackend, chunk_tokens: int) -> list[str]:
    """Probe a normal chunk and an over-context input; return warnings for reports/CLI."""
    notes: list[str] = []
    probe = "security evidence " * max(1, int(chunk_tokens))
    try:
        backend.embed([probe], "passage")
    except Exception as exc:
        notes.append(f"Embedding context probe for configured chunk size failed: {exc}")
    details = backend.details()
    context = details.get("embedding_context_length")
    if context:
        long_probe = "context probe " * (int(context) + max(1, int(chunk_tokens)))
        try:
            backend.embed([long_probe], "passage")
            notes.append("Over-context probe was accepted; truncation behavior could not be confirmed by the endpoint.")
        except Exception as exc:
            if "HTTP 400" in str(exc) or "HTTP 413" in str(exc):
                notes.append("Over-context probe was rejected by the endpoint with truncate=false, as expected.")
            else:
                notes.append(f"Over-context probe could not verify truncation behavior: {exc}")
    else:
        notes.append("Embedding context length is not reported; over-context truncation cannot be verified.")
    for note in notes:
        # With truncate=false, a 400 response to the deliberately oversized
        # negative probe is the expected confirmation that the server rejects
        # over-context input. Keep it in returned metadata, but don't present
        # it like the normal chunk failed.
        if "Over-context probe was rejected" not in note:
            warnings.warn(note, RuntimeWarning, stacklevel=2)
    return notes
