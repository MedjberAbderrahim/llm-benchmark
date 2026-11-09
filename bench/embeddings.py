"""Local/self-hosted embedding adapters and deterministic test backend."""
from __future__ import annotations

import hashlib
import math
from typing import Any, Protocol

import httpx
import numpy as np


class EmbeddingError(RuntimeError):
    pass


class EmbeddingBackend(Protocol):
    model: str
    def embed(self, texts: list[str], input_type: str = "passage") -> list[np.ndarray]: ...
    def details(self) -> dict[str, Any]: ...


class OllamaEmbeddingBackend:
    def __init__(self, base_url: str, model: str, timeout: float = 300, query_prefix: str = "", passage_prefix: str = ""):
        self.base_url, self.model = base_url.rstrip("/"), model
        self.query_prefix, self.passage_prefix = query_prefix, passage_prefix
        self.client = httpx.Client(timeout=timeout)
        self.dimension: int | None = None

    def embed(self, texts: list[str], input_type: str = "passage") -> list[np.ndarray]:
        prefix = self.query_prefix if input_type == "query" else self.passage_prefix
        try:
            response = self.client.post(f"{self.base_url}/api/embed", json={"model": self.model, "input": [prefix + text for text in texts]})
            response.raise_for_status()
            payload = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise EmbeddingError(f"Ollama embeddings failed at {self.base_url}: {exc}. Confirm Ollama is running and run `ollama pull {self.model}`.") from exc
        vectors = payload.get("embeddings")
        if not isinstance(vectors, list) or len(vectors) != len(texts):
            raise EmbeddingError("Ollama returned an unexpected embedding batch")
        return [_normalize(np.asarray(vector, dtype=np.float32)) for vector in vectors]

    def details(self) -> dict[str, Any]:
        details: dict[str, Any] = {"embedding_backend": "ollama", "embedding_model": self.model,
                                   "embedding_dimension": self.dimension, "embedding_digest": None,
                                   "embedding_quantization": None,
                                   "query_prefix": self.query_prefix, "passage_prefix": self.passage_prefix}
        try:
            models = self.client.get(f"{self.base_url}/api/tags", timeout=5).json().get("models", [])
            for item in models:
                if item.get("name") == self.model or item.get("model") == self.model:
                    details["embedding_digest"] = item.get("digest")
                    details["embedding_quantization"] = (item.get("details") or {}).get("quantization_level")
                    break
        except (httpx.HTTPError, ValueError):
            pass
        return details


class OpenAIEmbeddingBackend:
    def __init__(self, base_url: str, api_key: str | None, model: str, timeout: float = 300,
                 query_prefix: str = "", passage_prefix: str = ""):
        normalized = base_url.rstrip("/")
        self.base_url = normalized if normalized.endswith("/v1") else normalized + "/v1"
        self.model = model
        self.query_prefix, self.passage_prefix = query_prefix, passage_prefix
        headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
        self.client = httpx.Client(timeout=timeout, headers=headers)
        self.dimension: int | None = None

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
        return [_normalize(np.asarray(item["embedding"], dtype=np.float32)) for item in data]

    def details(self) -> dict[str, Any]:
        return {"embedding_backend": "openai", "embedding_model": self.model, "embedding_dimension": self.dimension,
                "embedding_digest": None, "embedding_quantization": None,
                "query_prefix": self.query_prefix, "passage_prefix": self.passage_prefix}


class HashEmbeddingBackend:
    """Deterministic offline embedding fake for tests; not semantically meaningful."""
    def __init__(self, model: str = "fake-hash", dimension: int = 64):
        self.model, self.dimension = model, dimension

    def embed(self, texts: list[str], input_type: str = "passage") -> list[np.ndarray]:
        vectors = []
        for text in texts:
            vector = np.zeros(self.dimension, dtype=np.float32)
            for token in text.lower().split():
                digest = hashlib.sha256(token.encode()).digest()
                index = int.from_bytes(digest[:4], "little") % self.dimension
                vector[index] += 1 if digest[4] & 1 else -1
            vectors.append(_normalize(vector))
        return vectors

    def details(self) -> dict[str, Any]:
        return {"embedding_backend": "fake", "embedding_model": self.model, "embedding_dimension": self.dimension}


def _normalize(vector: np.ndarray) -> np.ndarray:
    norm = float(np.linalg.norm(vector))
    if norm:
        vector = vector / norm
    return vector.astype(np.float32)
