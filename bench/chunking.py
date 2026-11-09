"""Lossless structure-aware chunks for retrieval."""
from __future__ import annotations

import hashlib
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    file: str
    text: str
    start_char: int
    end_char: int
    start_line: int
    end_line: int
    heading_path: tuple[str, ...]
    header: str | None = None  # CSV header metadata, deliberately outside text/quote matching


def estimate_tokens(text: str) -> int:
    return max(1, len(text.encode("utf-8")) // 4) if text else 0


def _section_path(lines: list[str], index: int, suffix: str) -> tuple[str, ...]:
    path: list[str] = []
    if suffix in {".md", ".markdown"}:
        for line in lines[:index + 1]:
            match = re.match(r"^(#{1,6})\s+(.+?)\s*#*\s*$", line)
            if match:
                level = len(match.group(1))
                path = path[:level - 1] + [match.group(2)]
    elif suffix == ".ini":
        for line in lines[:index + 1]:
            match = re.match(r"^\s*\[([^]]+)\]", line)
            if match:
                path = [match.group(1)]
    else:
        for line in lines[:index + 1]:
            match = re.match(r"^([A-Za-z_][\w.-]*)\s*:\s*(?:#.*)?$", line)
            if match:
                path = [match.group(1)]
    return tuple(path)


def _line_starts(text: str) -> list[int]:
    return [0] + [match.end() for match in re.finditer("\n", text)]


def _make_chunk(file: str, text: str, start: int, end: int, starts: list[int],
                path: tuple[str, ...], header: str | None = None) -> Chunk:
    start_line = max(1, sum(1 for pos in starts if pos <= start))
    end_line = max(start_line, sum(1 for pos in starts if pos < end))
    content = text[start:end]
    digest = hashlib.sha256(f"{file}\0{start}\0{end}\0{content}".encode()).hexdigest()[:20]
    return Chunk(digest, file, content, start, end, start_line, end_line, path, header)


def chunk_text(file: str, text: str, target_tokens: int = 400, overlap_tokens: int = 60,
               min_chunk_tokens: int = 40) -> list[Chunk]:
    if target_tokens < 1 or overlap_tokens < 0 or overlap_tokens >= target_tokens:
        raise ValueError("Require target_tokens > overlap_tokens >= 0")
    suffix = Path(file).suffix.lower()
    lines = text.splitlines(keepends=True)
    if not lines:
        return [_make_chunk(file, text, 0, 0, [0], ())]
    starts = _line_starts(text)
    if suffix == ".csv":
        header = lines[0].rstrip("\r\n")
        data_start = len(lines[0])
        row_idx = 1
        chunks: list[Chunk] = []
        while row_idx < len(lines):
            begin_idx = row_idx
            begin = starts[begin_idx]
            byte_count = 0
            while row_idx < len(lines) and (byte_count < target_tokens * 4 or row_idx == begin_idx):
                byte_count += len(lines[row_idx].encode("utf-8"))
                row_idx += 1
            end = starts[row_idx] if row_idx < len(starts) else len(text)
            chunks.append(_make_chunk(file, text, begin, end, starts, (), header))
        if not chunks:
            chunks.append(_make_chunk(file, text, data_start, len(text), starts, (), header))
        return chunks

    # Markdown and native configs first split at meaningful boundaries; oversized
    # sections are divided by line windows with source offsets retained.
    boundaries = [0]
    if suffix in {".md", ".markdown"}:
        for idx in range(1, len(lines)):
            if not lines[idx - 1].strip() or re.match(r"^#{1,6}\s", lines[idx]):
                pos = starts[idx]
                if pos > boundaries[-1]:
                    boundaries.append(pos)
    else:
        for idx in range(1, len(lines)):
            line = lines[idx]
            is_section = bool(re.match(r"^\s*\[[^]]+\]\s*$", line)) if suffix == ".ini" else bool(re.match(r"^[A-Za-z_][\w.-]*\s*:\s*(?:#.*)?$", line))
            if is_section and starts[idx] > boundaries[-1]:
                boundaries.append(starts[idx])
    if boundaries[-1] != len(text):
        boundaries.append(len(text))
    atomic: list[tuple[int, int]] = list(zip(boundaries[:-1], boundaries[1:]))
    packed: list[tuple[int, int]] = []
    start = atomic[0][0]
    end = start
    for a, b in atomic:
        if end > start and estimate_tokens(text[start:b]) > target_tokens:
            packed.append((start, end))
            start = a
        end = b
    if end > start or not packed:
        packed.append((start, end))

    # Split oversized packed regions at line boundaries; overlap is applied by
    # extending the next chunk's start into the preceding source region.
    raw_ranges: list[tuple[int, int]] = []
    char_target = target_tokens * 4
    char_overlap = overlap_tokens * 4
    for a, b in packed:
        if b - a <= char_target:
            raw_ranges.append((a, b))
            continue
        cursor = a
        while cursor < b:
            limit = min(b, cursor + char_target)
            if limit < b:
                newline = text.rfind("\n", cursor, limit)
                if newline > cursor:
                    limit = newline + 1
            if limit <= cursor:
                limit = min(b, cursor + char_target)
            raw_ranges.append((cursor, limit))
            if limit >= b:
                break
            next_cursor = max(cursor + 1, limit - char_overlap)
            # Start at the overlap line break itself. Starting one character
            # after it leaves that newline uncovered because source ranges use
            # an exclusive end offset.
            newline = text.find("\n", next_cursor, limit + 1)
            cursor = newline if newline >= 0 else next_cursor
    chunks: list[Chunk] = []
    for a, b in raw_ranges:
        piece = text[a:b]
        if estimate_tokens(piece) < min_chunk_tokens and chunks and b == len(text):
            prev = chunks.pop()
            chunks.append(_make_chunk(file, text, prev.start_char, b, starts,
                                      _section_path(lines, prev.start_line - 1, suffix)))
        else:
            line_idx = max(0, sum(1 for pos in starts if pos <= a) - 1)
            chunks.append(_make_chunk(file, text, a, b, starts, _section_path(lines, line_idx, suffix)))
    return chunks


def chunk_dict(chunk: Chunk) -> dict[str, object]:
    result = asdict(chunk)
    result["heading_path"] = list(chunk.heading_path)
    return result
