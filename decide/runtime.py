from __future__ import annotations

import asyncio
import os
import uuid
from typing import Any, Dict, Iterable, Mapping, Optional

from .health import latest_health
from .providers.base import ProviderResult
from .providers.registry import ProviderRegistry
from .selection import BenchmarkStore, SelectionPolicy, choose_model
from .telemetry import TelemetryStore


class DecisionRuntime:
    def __init__(self) -> None:
        self.providers = ProviderRegistry()
        self.benchmarks = BenchmarkStore()
        self.telemetry = TelemetryStore()
        configured_default = os.getenv("SYSTEMONE_DEFAULT_PROVIDER", "").strip()
        self.default_provider = configured_default or self.providers.first_name()

    async def decide(
        self,
        *,
        state: Any,
        questions: Mapping[str, Dict[str, Any]],
        provider: Optional[str] = None,
        model: Optional[str] = None,
        policy: Optional[SelectionPolicy] = None,
        ensemble: Optional[Iterable[str]] = None,
        request_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        rid = request_id or str(uuid.uuid4())

        if ensemble:
            results = await asyncio.gather(
                *[
                    self._invoke(name, state, questions, model=model, request_id=rid)
                    for name in ensemble
                ],
                return_exceptions=True,
            )
            successes = [r for r in results if isinstance(r, ProviderResult)]
            if not successes:
                errors = [str(r) for r in results]
                raise RuntimeError(f"all ensemble provider instances failed: {errors}")
            merged = _merge_results(successes)
            return {
                "request_id": rid,
                "route": {"mode": "ensemble", "providers": [r.provider for r in successes]},
                **merged,
            }

        selected_provider = provider
        selected_model = model
        if selected_provider is None and policy is not None:
            selected = choose_model(
                self.benchmarks.load(),
                policy,
                capabilities=self.providers.capability_profiles(),
                health=latest_health(self.telemetry.read(limit=10000)),
            )
            selected_provider = selected.provider
            selected_model = selected.model

        selected_provider = selected_provider or self.default_provider
        if not selected_provider:
            raise RuntimeError(
                "no provider instance is configured; set SYSTEMONE_PROVIDER_IDS "
                "or specify a provider registered by the host application"
            )

        result = await self._invoke(
            selected_provider,
            state,
            questions,
            model=selected_model,
            request_id=rid,
        )
        return {
            "request_id": rid,
            "route": {
                "mode": "single",
                "provider": result.provider,
                "model": result.model,
            },
            "answers": result.answers,
            "usage": result.usage,
            "latency_ms": result.latency_ms,
        }

    async def batch(self, requests: Iterable[Dict[str, Any]]) -> list[Dict[str, Any]]:
        async def run(item: Dict[str, Any]) -> Dict[str, Any]:
            policy = item.get("policy")
            selection = SelectionPolicy(**policy) if isinstance(policy, dict) else None
            return await self.decide(
                state=item["state"],
                questions=item["questions"],
                provider=item.get("provider"),
                model=item.get("model"),
                policy=selection,
                ensemble=item.get("ensemble"),
                request_id=item.get("request_id"),
            )

        return list(await asyncio.gather(*(run(item) for item in requests)))

    async def _invoke(
        self,
        provider_name: str,
        state: Any,
        questions: Mapping[str, Dict[str, Any]],
        *,
        model: Optional[str],
        request_id: str,
    ) -> ProviderResult:
        provider = self.providers.get(provider_name)
        try:
            result = await provider.decide(
                state,
                questions,
                model=model,
                idempotency_key=request_id,
            )
        except Exception as exc:
            self.telemetry.record({
                "request_id": request_id,
                "provider": provider_name,
                "model": model,
                "status": "error",
                "error": type(exc).__name__,
            })
            raise

        self.telemetry.record({
            "request_id": request_id,
            "provider": result.provider,
            "model": result.model,
            "status": "ok",
            "latency_ms": result.latency_ms,
            "usage": result.usage,
            "question_types": [q.get("type") for q in questions.values()],
        })
        return result


def _merge_results(results: list[ProviderResult]) -> Dict[str, Any]:
    question_ids = set()
    for result in results:
        question_ids.update(result.answers)

    merged: Dict[str, Dict[str, Any]] = {}
    for qid in question_ids:
        answers = [r.answers[qid] for r in results if qid in r.answers]
        if not answers:
            continue
        qtype = answers[0].get("type")
        if qtype == "choice":
            labels = set()
            for answer in answers:
                labels.update((answer.get("probabilities") or {}).keys())
            probs = {
                label: sum(float((a.get("probabilities") or {}).get(label, 0.0)) for a in answers) / len(answers)
                for label in labels
            }
            value = max(probs, key=probs.get)
            merged[qid] = {
                "type": "choice",
                "value": value,
                "probabilities": probs,
                "confidence": probs[value],
            }
        elif qtype in {"null", "noul"}:
            values = [float(a.get("value", a.get("noul", 0.0))) for a in answers]
            p = sum(values) / len(values)
            merged[qid] = {"type": "null", "value": p, "confidence": max(p, 1.0 - p)}
        elif qtype == "score":
            values = [float(a.get("value", a.get("score", 0.0))) for a in answers]
            merged[qid] = {
                "type": "score",
                "value": sum(values) / len(values),
                "confidence": sum(float(a.get("confidence", 0.0)) for a in answers) / len(answers),
            }
        else:
            merged[qid] = answers[0]

    return {
        "answers": merged,
        "usage": {
            "prompt_tokens": sum(r.usage.get("prompt_tokens", 0) for r in results),
            "completion_tokens": sum(r.usage.get("completion_tokens", 0) for r in results),
            "total_tokens": sum(r.usage.get("total_tokens", 0) for r in results),
        },
        "latency_ms": max(r.latency_ms for r in results),
    }
