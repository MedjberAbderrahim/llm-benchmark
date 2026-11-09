from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any

import httpx

from .schemas import OUTPUT_JSON_SCHEMA


class BackendError(RuntimeError):
    pass


@dataclass
class Completion:
    content: str
    wall_seconds: float
    time_to_first_token_seconds: float | None
    metrics: dict[str, Any]


class Backend:
    def set_timeout(self, seconds: float | None) -> None:
        """Set a request timeout for one case, or restore the backend default."""
        self.timeout = 600.0 if seconds is None else seconds

    def generate(self, messages: list[dict[str, str]]) -> Completion:
        raise NotImplementedError

    def warmup(self) -> Completion:
        return self.generate([{"role": "user", "content": "Reply with OK."}])

    def prompt_token_count(self, messages: list[dict[str, str]]) -> tuple[int, str]:
        raise NotImplementedError

    def environment_details(self) -> dict[str, Any]:
        return {}


class OllamaBackend(Backend):
    def __init__(self, base_url: str, model: str, temperature: float, seed: int,
                 num_ctx: int, max_output_tokens: int, keep_alive: str, timeout: float = 600.0):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.options = {"temperature": temperature, "seed": seed, "num_ctx": num_ctx,
                        "num_predict": max_output_tokens}
        self.keep_alive = keep_alive
        self.timeout = timeout
        self.client = httpx.Client(timeout=timeout)

    def generate(self, messages: list[dict[str, str]]) -> Completion:
        body = {"model": self.model, "messages": messages, "stream": False,
                "format": OUTPUT_JSON_SCHEMA, "options": self.options, "keep_alive": self.keep_alive}
        started = time.perf_counter()
        try:
            response = self.client.post(f"{self.base_url}/api/chat", json=body, timeout=self.timeout)
            response.raise_for_status()
            payload = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise BackendError(self._explain_error(exc)) from exc
        wall = time.perf_counter() - started
        content = payload.get("message", {}).get("content", "")
        return Completion(content=content, wall_seconds=wall, time_to_first_token_seconds=None,
                          metrics={key: payload.get(key) for key in (
                              "total_duration", "load_duration", "prompt_eval_count", "prompt_eval_duration",
                              "eval_count", "eval_duration")})

    def warmup(self) -> Completion:
        body = {"model": self.model, "messages": [{"role": "user", "content": "Reply with OK."}], "stream": False,
                "options": {**self.options, "num_predict": min(int(self.options["num_predict"]), 4)},
                "keep_alive": self.keep_alive}
        started = time.perf_counter()
        try:
            response = self.client.post(f"{self.base_url}/api/chat", json=body)
            response.raise_for_status()
            payload = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise BackendError(self._explain_error(exc)) from exc
        return Completion(payload.get("message", {}).get("content", ""), time.perf_counter() - started, None,
                          {key: payload.get(key) for key in (
                              "total_duration", "load_duration", "prompt_eval_count", "prompt_eval_duration",
                              "eval_count", "eval_duration")})

    def prompt_token_count(self, messages: list[dict[str, str]]) -> tuple[int, str]:
        prompt = "\n".join(f"{m['role']}: {m['content']}" for m in messages)
        try:
            response = self.client.post(f"{self.base_url}/api/tokenize", json={"model": self.model, "prompt": prompt}, timeout=20)
            response.raise_for_status()
            payload = response.json()
            tokens = payload.get("tokens")
            if isinstance(tokens, list):
                return len(tokens), "ollama_tokenize"
            if isinstance(tokens, int):
                return tokens, "ollama_tokenize"
        except (httpx.HTTPError, ValueError):
            pass
        return max(1, len(prompt.encode("utf-8")) // 4), "character_estimate_4_bytes_per_token"

    def environment_details(self) -> dict[str, Any]:
        result: dict[str, Any] = {"backend_version": None, "model_digest": None, "quantization": None,
                                  "model_size_bytes": None}
        try:
            version = self.client.get(f"{self.base_url}/api/version", timeout=5).json()
            result["backend_version"] = version.get("version")
        except (httpx.HTTPError, ValueError):
            pass
        try:
            listing = self.client.get(f"{self.base_url}/api/tags", timeout=10).json().get("models", [])
            for item in listing:
                if item.get("name") == self.model or item.get("model") == self.model:
                    result["model_digest"] = item.get("digest")
                    result["model_size_bytes"] = item.get("size")
                    details = item.get("details") or {}
                    result["quantization"] = details.get("quantization_level")
                    break
        except (httpx.HTTPError, ValueError):
            pass
        try:
            show = self.client.post(f"{self.base_url}/api/show", json={"model": self.model}, timeout=20).json()
            details = show.get("details") or {}
            result["quantization"] = result["quantization"] or details.get("quantization_level")
            result["model_family"] = details.get("family")
            result["model_parameters"] = details.get("parameter_size")
            result["model_size_bytes"] = result["model_size_bytes"] or show.get("size")
        except (httpx.HTTPError, ValueError):
            pass
        return result

    def _explain_error(self, exc: Exception) -> str:
        if isinstance(exc, httpx.ConnectError):
            return (f"Cannot reach Ollama at {self.base_url}. Start Ollama (`ollama serve`) and confirm it is listening. "
                    f"Then pull the model with `ollama pull {self.model}`. Details: {exc}")
        response = getattr(exc, "response", None)
        if response is not None and response.status_code == 404:
            return f"Ollama could not find model {self.model!r}; run `ollama pull {self.model}`. Response: {response.text[:500]}"
        return f"Ollama request to {self.base_url} failed: {exc}"


class OpenAICompatibleBackend(Backend):
    def __init__(self, base_url: str, api_key: str | None, model: str, temperature: float,
                 seed: int, max_output_tokens: int, timeout: float = 600.0):
        normalized = base_url.rstrip("/")
        if normalized.endswith("/chat/completions"):
            self.endpoint = normalized
            self.base_url = normalized.rsplit("/chat/completions", 1)[0]
        else:
            if not normalized.endswith("/v1"):
                normalized += "/v1"
            self.base_url = normalized
            self.endpoint = f"{normalized}/chat/completions"
        self.model = model
        self.temperature = temperature
        self.seed = seed
        self.max_output_tokens = max_output_tokens
        self.timeout = timeout
        headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
        self.client = httpx.Client(timeout=timeout, headers=headers)

    def generate(self, messages: list[dict[str, str]]) -> Completion:
        body: dict[str, Any] = {"model": self.model, "messages": messages, "temperature": self.temperature,
                                "seed": self.seed, "max_tokens": self.max_output_tokens,
                                "response_format": {"type": "json_object"}, "stream": True,
                                "stream_options": {"include_usage": True}}
        started = time.perf_counter()
        first_token: float | None = None
        chunks: list[str] = []
        usage: dict[str, Any] = {}
        try:
            with self.client.stream("POST", self.endpoint, json=body, timeout=self.timeout) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if not line or not line.startswith("data:"):
                        continue
                    data = line[5:].strip()
                    if data == "[DONE]":
                        break
                    payload = json.loads(data)
                    if payload.get("usage"):
                        usage = payload["usage"]
                    choices = payload.get("choices") or []
                    if choices:
                        delta = choices[0].get("delta", {})
                        piece = delta.get("content")
                        if piece:
                            if first_token is None:
                                first_token = time.perf_counter() - started
                            chunks.append(piece)
        except (httpx.HTTPError, ValueError) as exc:
            response = getattr(exc, "response", None)
            if response is not None and response.status_code == 401:
                detail = "Check --api-key or disable authentication on the local server."
            else:
                detail = "Check --base-url and that the OpenAI-compatible server is running."
            raise BackendError(f"OpenAI-compatible request to {self.endpoint} failed. {detail} Details: {exc}") from exc
        return Completion(content="".join(chunks), wall_seconds=time.perf_counter() - started,
                          time_to_first_token_seconds=first_token,
                          metrics={"prompt_tokens": usage.get("prompt_tokens"),
                                   "completion_tokens": usage.get("completion_tokens"),
                                   "total_tokens": usage.get("total_tokens")})

    def warmup(self) -> Completion:
        body = {"model": self.model, "messages": [{"role": "user", "content": "Reply with OK."}],
                "temperature": self.temperature, "seed": self.seed, "max_tokens": min(self.max_output_tokens, 4),
                "stream": True, "stream_options": {"include_usage": True}}
        started = time.perf_counter()
        first_token = None
        chunks: list[str] = []
        usage: dict[str, Any] = {}
        try:
            with self.client.stream("POST", self.endpoint, json=body) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if not line or not line.startswith("data:"):
                        continue
                    data = line[5:].strip()
                    if data == "[DONE]":
                        break
                    payload = json.loads(data)
                    if payload.get("usage"):
                        usage = payload["usage"]
                    choices = payload.get("choices") or []
                    if choices:
                        piece = choices[0].get("delta", {}).get("content")
                        if piece:
                            if first_token is None:
                                first_token = time.perf_counter() - started
                            chunks.append(piece)
        except (httpx.HTTPError, ValueError) as exc:
            raise BackendError(f"OpenAI-compatible warm-up failed at {self.endpoint}: {exc}") from exc
        return Completion("".join(chunks), time.perf_counter() - started, first_token,
                          {"prompt_tokens": usage.get("prompt_tokens"),
                           "completion_tokens": usage.get("completion_tokens"),
                           "total_tokens": usage.get("total_tokens")})

    def prompt_token_count(self, messages: list[dict[str, str]]) -> tuple[int, str]:
        # The OpenAI-compatible server reports the exact prompt count after inference.
        # Before the call, estimate conservatively for a truncation warning.
        prompt = "\n".join(f"{m['role']}: {m['content']}" for m in messages)
        return max(1, len(prompt.encode("utf-8")) // 4), "character_estimate_4_bytes_per_token"

    def environment_details(self) -> dict[str, Any]:
        result: dict[str, Any] = {"backend_version": None, "model_digest": None, "quantization": None,
                                  "backend_model_tag": None}
        try:
            listing = self.client.get(f"{self.base_url}/models", timeout=10).json().get("data", [])
            for item in listing:
                if item.get("id") == self.model:
                    result["backend_model_tag"] = item.get("id")
                    break
        except (httpx.HTTPError, ValueError):
            pass
        server_root = self.base_url.removesuffix("/v1")
        for version_url in (f"{server_root}/version", f"{server_root}/api/version"):
            try:
                version_response = self.client.get(version_url, timeout=5)
                if version_response.is_success:
                    payload = version_response.json()
                    if isinstance(payload, dict):
                        result["backend_version"] = payload.get("version") or payload.get("build")
                    else:
                        result["backend_version"] = str(payload)
                    break
            except (httpx.HTTPError, ValueError):
                continue
        result["backend_note"] = "OpenAI-compatible API has no standard model digest or quantization field."
        return result


def create_backend(config: dict[str, Any]) -> Backend:
    if config["backend"] == "ollama":
        return OllamaBackend(config["base_url"], config["model"], config["temperature"], config["seed"],
                             config["num_ctx"], config["max_output_tokens"], config["keep_alive"])
    if config["backend"] == "openai":
        return OpenAICompatibleBackend(config["base_url"], config.get("api_key"), config["model"],
                                       config["temperature"], config["seed"], config["max_output_tokens"])
    raise ValueError(f"Unsupported backend {config['backend']!r}; use ollama or openai")
