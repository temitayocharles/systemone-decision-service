import os
from typing import List

import requests

from .config import get_setting


class EmbeddingClient:
    def __init__(self) -> None:
        self.provider = get_setting("LLM_PROVIDER", "ollama").lower()
        self.model = get_setting("EMBED_MODEL", "nomic-embed-text")
        self.ollama_host = get_setting("OLLAMA_HOST", "http://localhost:11434")

    def embed(self, text: str) -> List[float]:
        if self.provider == "ollama":
            payload = {"model": self.model, "input": text}
            resp = requests.post(f"{self.ollama_host}/api/embed", json=payload, timeout=60)
            resp.raise_for_status()
            data = resp.json()
            if isinstance(data, dict):
                items = data.get("embeddings") or data.get("embedding") or []
                if isinstance(items, list) and items and isinstance(items[0], list):
                    return items[0]
                if isinstance(items, list) and items and isinstance(items[0], (int, float)):
                    return items
            raise ValueError("Unexpected Ollama embed response")

        raise ValueError(f"Unsupported embedding provider: {self.provider}")
