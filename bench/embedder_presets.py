"""Named embedding configurations used by the CLI and comparison reports."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


DEFAULT_QUERY_INSTRUCTION = (
    "Given a compliance control or requirement, retrieve the evidence passages "
    "(policies, procedures, configuration excerpts) that show whether it is met"
)


@dataclass(frozen=True)
class EmbedderPreset:
    name: str
    model: str
    query_prefix: str = ""
    passage_prefix: str = ""
    query_prefix_template: str | None = None
    supports_matryoshka: bool = False
    description: str = ""


PRESETS: dict[str, EmbedderPreset] = {
    "bge-m3": EmbedderPreset("bge-m3", "bge-m3", description="Multilingual baseline; raw queries and passages."),
    "qwen3-embed-8b": EmbedderPreset(
        "qwen3-embed-8b", "qwen3-embedding:8b",
        query_prefix_template="Instruct: {instruction}\nQuery: ",
        supports_matryoshka=True,
        description="Qwen retrieval instruction is applied to queries only; passages remain raw."),
    "nemotron-embed-8b": EmbedderPreset(
        "nemotron-embed-8b", "maternion/nemotron-3.5-embed:8b-q4_k_m",
        query_prefix="query: ", passage_prefix="passage: ", supports_matryoshka=True,
        description="Nemotron's documented task prefixes; both query and passage prefixes are required."),
}


def resolve_embedder(preset: str | None = None, model: str | None = None,
                     query_prefix: str | None = None, passage_prefix: str | None = None,
                     query_instruction: str | None = None,
                     embed_dim: int | None = None) -> dict[str, Any]:
    name = preset or "bge-m3"
    if name not in PRESETS:
        raise ValueError(f"Unknown embedder preset {name!r}; choose from: {', '.join(PRESETS)}")
    selected = PRESETS[name]
    instruction = query_instruction or DEFAULT_QUERY_INSTRUCTION
    default_query = (selected.query_prefix_template.format(instruction=instruction)
                     if selected.query_prefix_template else selected.query_prefix)
    if embed_dim is not None:
        if not selected.supports_matryoshka:
            raise ValueError(f"Embedder preset {name!r} does not support --embed-dim")
        if embed_dim < 1:
            raise ValueError("--embed-dim must be positive")
    return {"embedder": name, "embed_model": model or selected.model,
            "query_prefix": default_query if query_prefix is None else query_prefix,
            "passage_prefix": selected.passage_prefix if passage_prefix is None else passage_prefix,
            "query_instruction": instruction, "embed_dim": embed_dim,
            "supports_matryoshka": selected.supports_matryoshka,
            "preset_model": selected.model}
