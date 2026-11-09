from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from pathlib import Path
from typing import Any


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def dataset_hash(root: Path) -> str:
    digest = hashlib.sha256()
    paths = [root / "data" / "labels.yaml"]
    paths += sorted((root / "data" / "controls").glob("*.yaml"))
    paths += sorted(p for p in (root / "data" / "evidence").rglob("*") if p.is_file())
    for path in paths:
        relative = path.relative_to(root).as_posix()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def normalize_quote(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = text.translate(str.maketrans({
        "‘": "'", "’": "'", "“": '"', "”": '"', "„": '"', "–": "-", "—": "-", "…": "...",
    }))
    return re.sub(r"\s+", " ", text).strip().casefold()


def strip_json_fence(content: str) -> str:
    value = content.strip()
    if value.startswith("```"):
        value = re.sub(r"^```(?:json)?\s*", "", value, flags=re.IGNORECASE)
        value = re.sub(r"\s*```$", "", value)
    return value.strip()


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")
