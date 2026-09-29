from __future__ import annotations

from typing import List, Sequence

import requests

from .config import get_setting


class EmbeddingClient:
    def __init__(self) -> None:
        self.provider = get_setting("LLM_PROVIDER", "ollama").lower()
        self.model = get_setting("EMBED_MODEL", "nomic-embed-text")
        self.ollama_host = get_setting("OLLAMA_HOST", "http://localhost:11434")
        self.batch_size = int(get_setting("EMBED_BATCH_SIZE", "32"))

    def _ollama_embed(self, inputs: Sequence[str]) -> List[List[float]]:
        payload = {"model": self.model, "input": list(inputs)}
        resp = requests.post(
            f"{self.ollama_host}/api/embed",
            json=payload,
            timeout=120,
        )
        resp.raise_for_status()
        data = resp.json()
        embeddings = data.get("embeddings") if isinstance(data, dict) else None
        if not isinstance(embeddings, list) or len(embeddings) != len(inputs):
            raise ValueError("Unexpected Ollama batch embed response")
        if embeddings and not isinstance(embeddings[0], list):
            raise ValueError("Unexpected Ollama batch embed response")
        return embeddings

    def embed_many(self, texts: Sequence[str]) -> List[List[float]]:
        items = list(texts)
        if not items:
            return []
        if self.provider != "ollama":
            raise ValueError(f"Unsupported embedding provider: {self.provider}")

        output: List[List[float]] = []
        batch_size = max(1, self.batch_size)
        for start in range(0, len(items), batch_size):
            output.extend(self._ollama_embed(items[start:start + batch_size]))
        return output

    def embed(self, text: str) -> List[float]:
        return self.embed_many([text])[0]
