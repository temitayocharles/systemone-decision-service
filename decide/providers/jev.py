from __future__ import annotations

import time
from typing import Any, Dict, Mapping, Optional

import httpx

from .base import DecisionProvider, ProviderResult


class JevProvider(DecisionProvider):
    """Optional native System One adapter, configured only when explicitly declared."""

    def __init__(
        self,
        *,
        name: str,
        base_url: str,
        model: str,
        api_key: str = "",
        timeout_s: float = 20.0,
    ) -> None:
        self.name = name
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.default_model = model
        self.timeout_s = float(timeout_s)

    async def decide(
        self,
        state: Any,
        questions: Mapping[str, Dict[str, Any]],
        *,
        model: Optional[str] = None,
        idempotency_key: Optional[str] = None,
    ) -> ProviderResult:
        if not self.base_url:
            raise RuntimeError(f"provider instance {self.name!r} has no base URL configured")
        selected_model = model or self.default_model
        if not selected_model:
            raise RuntimeError(f"provider instance {self.name!r} has no model configured")

        payload = {
            "model": selected_model,
            "state": state,
            "questions": {qid: _to_jev_question(q) for qid, q in questions.items()},
        }
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key[:100]

        started = time.perf_counter()
        async with httpx.AsyncClient(timeout=self.timeout_s) as client:
            response = await client.post(
                f"{self.base_url}/v1/systemone",
                json=payload,
                headers=headers,
            )
        response.raise_for_status()
        data = response.json()
        return ProviderResult(
            provider=self.name,
            model=data.get("model", selected_model),
            answers={
                qid: _from_jev_answer(answer)
                for qid, answer in (data.get("answers") or {}).items()
            },
            usage=_normalize_usage(data.get("usage") or {}),
            latency_ms=int((time.perf_counter() - started) * 1000),
            raw=data,
        )


def _to_jev_question(question: Dict[str, Any]) -> Dict[str, Any]:
    q = dict(question)
    qtype = q.get("type")
    out: Dict[str, Any] = {
        "type": "noul" if qtype in {"null", "binary", "abstain"} else qtype,
        "instructions": q.get("instructions") or q.get("prompt") or "",
    }
    if out["type"] == "choice":
        out["criteria"] = q.get("criteria") or q.get("options") or {}
    elif out["type"] == "score":
        criteria = q.get("criteria")
        if criteria is None:
            labels = q.get("labels")
            if labels:
                criteria = [str(v) for v in labels]
            else:
                minimum = int(q.get("min", 0))
                maximum = int(q.get("max", 4))
                criteria = [str(v) for v in range(minimum, maximum + 1)]
        out["criteria"] = criteria
    elif q.get("criteria"):
        out["criteria"] = q["criteria"]
    return out


def _from_jev_answer(answer: Dict[str, Any]) -> Dict[str, Any]:
    qtype = answer.get("type")
    if qtype == "choice":
        return {
            "type": "choice",
            "value": answer.get("choice"),
            "probabilities": answer.get("probabilities") or {},
            "confidence": float(answer.get("confidence", 0.0)),
        }
    if qtype == "score":
        return {
            "type": "score",
            "value": answer.get("score"),
            "confidence": float(answer.get("confidence", 0.0)),
        }
    if qtype == "noul":
        p_yes = float(answer.get("noul", 0.0))
        return {
            "type": "null",
            "value": p_yes,
            "confidence": max(p_yes, 1.0 - p_yes),
        }
    return dict(answer)


def _normalize_usage(usage: Dict[str, Any]) -> Dict[str, int]:
    input_tokens = int(usage.get("input_tokens", 0) or 0)
    output_tokens = int(usage.get("output_tokens", 0) or 0)
    return {
        "prompt_tokens": input_tokens,
        "completion_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
    }
