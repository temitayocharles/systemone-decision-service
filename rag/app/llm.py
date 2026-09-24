from __future__ import annotations

import os
import time
from typing import Any, Dict, Tuple

import requests

from .config import get_setting


class LLMClient:
    def __init__(self) -> None:
        self.provider = get_setting("LLM_PROVIDER", "ollama").lower()
        self.model = get_setting("LLM_MODEL", "qwen2.5:3b")
        self.ollama_host = get_setting("OLLAMA_HOST", "http://localhost:11434")

    def generate(self, prompt: str) -> Tuple[str, int, int]:
        if self.provider == "ollama":
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.1},
            }
            start = time.time()
            response = requests.post(f"{self.ollama_host}/api/generate", json=payload, timeout=180)
            response.raise_for_status()
            data = response.json()
            answer = (data.get("response") or "").strip()
            tokens_in = int(data.get("prompt_eval_count") or 0)
            tokens_out = int(data.get("eval_count") or 0)
            return answer, tokens_in, tokens_out

        raise ValueError(f"Unsupported LLM provider: {self.provider}")
