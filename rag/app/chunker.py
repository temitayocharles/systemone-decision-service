from __future__ import annotations

import re
from pathlib import Path
from typing import List


def _clean_text(text: str) -> str:
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def chunk_markdown_file(path: Path, target_tokens: int = 650, overlap_tokens: int = 100) -> List[str]:
    text = path.read_text(encoding="utf-8")
    text = _clean_text(text)
    words = text.split()
    if not words:
        return []

    window = max(1, target_tokens)
    step = max(1, target_tokens - overlap_tokens)
    chunks: List[str] = []
    for i in range(0, len(words), step):
        window_words = words[i:i + window]
        if not window_words:
            continue
        chunks.append(" ".join(window_words))
        if len(window_words) < window:
            break
    return chunks


def chunk_directory(directory: Path) -> List[str]:
    chunks: List[str] = []
    for path in sorted(directory.glob("*.md")):
        chunks.extend(chunk_markdown_file(path))
    return chunks
