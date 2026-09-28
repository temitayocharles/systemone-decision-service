from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Mapping, Optional


@dataclass(frozen=True)
class ProviderResult:
    provider: str
    model: str
    answers: Dict[str, Dict[str, Any]]
    usage: Dict[str, int]
    latency_ms: int
    raw: Optional[Dict[str, Any]] = None


class DecisionProvider(ABC):
    name: str

    @abstractmethod
    async def decide(
        self,
        state: Any,
        questions: Mapping[str, Dict[str, Any]],
        *,
        model: Optional[str] = None,
        idempotency_key: Optional[str] = None,
    ) -> ProviderResult:
        raise NotImplementedError

    async def health(self) -> Dict[str, Any]:
        return {"provider": self.name, "status": "ok"}
