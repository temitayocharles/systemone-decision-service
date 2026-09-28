from __future__ import annotations

import time
from typing import Any, Dict, Mapping, Optional

from ..calibration_profiles import CalibrationProfileStore
from ..engine_v2 import ConfigurableScalableDecisionEngine
from .base import DecisionProvider, ProviderResult


class OpenAICompatibleProvider(DecisionProvider):
    def __init__(
        self,
        *,
        name: str,
        base_url: str,
        model: str,
        api_key: str = "",
        timeout_s: float = 60.0,
        max_parallel: int = 8,
    ) -> None:
        self.name = name
        self.base_url = base_url
        self.default_model = model
        self.api_key = api_key
        self.timeout_s = timeout_s
        self.max_parallel = max_parallel
        self._engines: Dict[str, ConfigurableScalableDecisionEngine] = {}

    def _temperatures_for(self, model: str) -> Dict[str, float]:
        temperatures: Dict[str, float] = {}
        store = CalibrationProfileStore()
        for question_type in ("choice", "score", "null"):
            profile = store.get(self.name, model, question_type)
            if profile is not None:
                temperatures[question_type] = profile.temperature
        return temperatures

    def _engine_for(self, model: str) -> ConfigurableScalableDecisionEngine:
        if model not in self._engines:
            temperatures = self._temperatures_for(model)
            if "null" in temperatures:
                temperatures["noul"] = temperatures["null"]
            self._engines[model] = ConfigurableScalableDecisionEngine(
                base_url=self.base_url,
                model=model,
                api_key=self.api_key,
                timeout_s=self.timeout_s,
                max_parallel=self.max_parallel,
                temperatures=temperatures or None,
            )
        return self._engines[model]

    async def refresh_calibration(self, model: Optional[str] = None) -> None:
        targets = [model] if model else list(self._engines)
        for target in targets:
            if not target:
                continue
            engine = self._engines.pop(target, None)
            if engine is not None:
                await engine.aclose()

    async def decide(
        self,
        state: Any,
        questions: Mapping[str, Dict[str, Any]],
        *,
        model: Optional[str] = None,
        idempotency_key: Optional[str] = None,
    ) -> ProviderResult:
        selected_model = model or self.default_model
        if not selected_model:
            raise RuntimeError(
                f"provider instance {self.name!r} has no model configured"
            )

        engine = self._engine_for(selected_model)
        started = time.perf_counter()
        normalized = {
            qid: _normalize_question(q)
            for qid, q in questions.items()
        }
        results, usage = await engine.decide(str(state), normalized)
        answers = {
            qid: _normalize_answer(answer)
            for qid, answer in results.items()
        }
        return ProviderResult(
            provider=self.name,
            model=selected_model,
            answers=answers,
            usage=usage,
            latency_ms=int((time.perf_counter() - started) * 1000),
        )

    async def aclose(self) -> None:
        for engine in self._engines.values():
            await engine.aclose()
        self._engines.clear()


def _normalize_question(question: Dict[str, Any]) -> Dict[str, Any]:
    q = dict(question)
    qtype = q.get("type")
    if "instructions" in q and "prompt" not in q:
        q["prompt"] = q["instructions"]

    # The public System One contract is "null". The low-level engine retains
    # its historical internal "noul" discriminator, so translate only at this
    # provider boundary and normalize the answer back on egress.
    if qtype in {"null", "noul", "binary", "abstain"}:
        q["type"] = "noul"

    if q["type"] == "choice" and "criteria" in q and "options" not in q:
        q["options"] = q["criteria"]
    if q["type"] == "score" and "criteria" in q and "labels" not in q:
        criteria = q["criteria"]
        q["min"] = 0
        q["max"] = max(1, len(criteria) - 1)
        q["labels"] = list(range(len(criteria)))
    return q


def _normalize_answer(answer: Dict[str, Any]) -> Dict[str, Any]:
    normalized = dict(answer)
    if normalized.get("type") == "noul":
        normalized["type"] = "null"
    return normalized
