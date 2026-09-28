from __future__ import annotations

import time
from typing import Any, Dict, Mapping, Optional

from ..engine_v2 import ScalableDecisionEngine
from .base import DecisionProvider, ProviderResult


class OpenAICompatibleProvider(DecisionProvider):
    name = "openai_compatible"

    def __init__(self) -> None:
        self.engine = ScalableDecisionEngine()

    async def decide(
        self,
        state: Any,
        questions: Mapping[str, Dict[str, Any]],
        *,
        model: Optional[str] = None,
        idempotency_key: Optional[str] = None,
    ) -> ProviderResult:
        started = time.perf_counter()
        normalized = {qid: _normalize_question(q) for qid, q in questions.items()}
        results, usage = await self.engine.decide(str(state), normalized)
        return ProviderResult(
            provider=self.name,
            model=model or "configured-openai-compatible-model",
            answers=results,
            usage=usage,
            latency_ms=int((time.perf_counter() - started) * 1000),
        )

    async def aclose(self) -> None:
        await self.engine.aclose()


def _normalize_question(question: Dict[str, Any]) -> Dict[str, Any]:
    q = dict(question)
    qtype = q.get("type")
    if "instructions" in q and "prompt" not in q:
        q["prompt"] = q["instructions"]
    if qtype in {"noul", "binary", "abstain"}:
        q["type"] = "null"
    if q["type"] == "choice" and "criteria" in q and "options" not in q:
        q["options"] = q["criteria"]
    if q["type"] == "score" and "criteria" in q and "labels" not in q:
        criteria = q["criteria"]
        q["min"] = 0
        q["max"] = max(1, len(criteria) - 1)
        q["labels"] = list(range(len(criteria)))
    return q
