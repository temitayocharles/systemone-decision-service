from __future__ import annotations

import time
from typing import Any, Dict, Mapping, Optional

from .. import config
from ..calibration_profiles import CalibrationProfileStore
from ..engine_v2 import ScalableDecisionEngine
from .base import DecisionProvider, ProviderResult


class OpenAICompatibleProvider(DecisionProvider):
    name = "openai_compatible"

    def __init__(self) -> None:
        self.model = config.MODEL
        self.engine = ScalableDecisionEngine()
        self._apply_calibration_profiles()

    def _apply_calibration_profiles(self) -> None:
        store = CalibrationProfileStore()
        for question_type in ("choice", "score", "null"):
            profile = store.get(self.name, self.model, question_type)
            if profile is not None:
                self.engine.temperatures[question_type] = profile.temperature

    async def decide(
        self,
        state: Any,
        questions: Mapping[str, Dict[str, Any]],
        *,
        model: Optional[str] = None,
        idempotency_key: Optional[str] = None,
    ) -> ProviderResult:
        requested_model = model or self.model
        if requested_model != self.model:
            raise RuntimeError(
                f"openai_compatible is configured for {self.model!r}; "
                f"requested model {requested_model!r} is not configured in this provider instance"
            )

        started = time.perf_counter()
        normalized = {qid: _normalize_question(q) for qid, q in questions.items()}
        results, usage = await self.engine.decide(str(state), normalized)
        return ProviderResult(
            provider=self.name,
            model=self.model,
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
