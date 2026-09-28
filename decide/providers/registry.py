from __future__ import annotations

import os
from typing import Dict, Iterable

from .base import DecisionProvider
from .jev import JevProvider
from .openai_compatible import OpenAICompatibleProvider


class ProviderRegistry:
    def __init__(self) -> None:
        self._providers: Dict[str, DecisionProvider] = {}
        configured = [
            p.strip()
            for p in os.getenv(
                "SYSTEMONE_PROVIDERS", "openai_compatible,jev"
            ).split(",")
            if p.strip()
        ]
        for name in configured:
            if name == "openai_compatible":
                self.register(OpenAICompatibleProvider())
            elif name == "jev":
                self.register(JevProvider())

    def register(self, provider: DecisionProvider) -> None:
        self._providers[provider.name] = provider

    def get(self, name: str) -> DecisionProvider:
        try:
            return self._providers[name]
        except KeyError as exc:
            raise KeyError(f"unknown provider: {name}") from exc

    def names(self) -> Iterable[str]:
        return tuple(self._providers)

    def items(self):
        return self._providers.items()
