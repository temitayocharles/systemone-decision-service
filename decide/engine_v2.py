from __future__ import annotations

import asyncio
from typing import Dict, List, Optional

import httpx

from .engine import DecisionEngine, EngineError


class ScalableDecisionEngine(DecisionEngine):
    """Decision engine without the old >9 candidate tournament approximation."""

    async def _evaluate_digit_labels(
        self,
        prompt: str,
        candidates: List[str],
        question_type: str,
        usage: Dict[str, int],
    ) -> List[float]:
        n = len(candidates)
        if n < 2:
            raise EngineError("at least two candidates are required")

        if n <= 9:
            return await super()._evaluate_digit_labels(
                prompt, candidates, question_type, usage
            )

        async def score(candidate: str) -> float:
            binary_prompt = (
                f"{prompt}\n\nCandidate:\n{candidate}\n\n"
                "Is this candidate the best answer to the question given the state? "
                "Answer with only YES or NO. No other text."
            )
            probs = await self._decide_labels(
                binary_prompt, ["YES", "NO"], question_type, usage
            )
            return float(probs[0])

        raw = list(await asyncio.gather(*(score(candidate) for candidate in candidates)))
        total = sum(raw)
        if total <= 0:
            return [1.0 / n] * n
        return [value / total for value in raw]


class ConfigurableScalableDecisionEngine(ScalableDecisionEngine):
    """A decision engine whose endpoint/model/auth are injected per provider instance."""

    def __init__(
        self,
        *,
        base_url: str,
        model: str,
        api_key: str = "",
        timeout_s: float = 60.0,
        max_parallel: int = 8,
        temperatures: Optional[Dict[str, float]] = None,
    ) -> None:
        super().__init__(temperatures=temperatures)
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_key = api_key
        self.timeout_s = float(timeout_s)
        self._sem = asyncio.Semaphore(int(max_parallel))

    async def _client_or_raise(self) -> httpx.AsyncClient:
        if not self.base_url:
            raise EngineError("provider base URL is not configured")
        if not self.model:
            raise EngineError("provider model is not configured")
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout_s,
            )
        return self._client

    async def _logprobs_for(
        self, prompt: str, usage: Dict[str, int]
    ) -> Dict[str, float]:
        client = await self._client_or_raise()
        body = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1,
            "temperature": 0,
            "logprobs": True,
            "top_logprobs": 20,
        }
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        try:
            resp = await client.post("/chat/completions", json=body, headers=headers)
        except httpx.HTTPError as exc:
            raise EngineError(f"provider request failed: {exc}") from exc

        if resp.status_code != 200:
            raise EngineError(
                f"provider returned HTTP {resp.status_code}: {resp.text[:300]}"
            )

        try:
            data = resp.json()
            choice = data["choices"][0]
            top = choice["logprobs"]["content"][0]["top_logprobs"]
        except (KeyError, IndexError, TypeError) as exc:
            raise EngineError(
                "provider did not return token logprobs; refusing to invent probabilities"
            ) from exc

        for key in ("prompt_tokens", "completion_tokens", "total_tokens"):
            value = (data.get("usage") or {}).get(key)
            if isinstance(value, int):
                usage[key] = usage.get(key, 0) + value

        return {item["token"]: float(item["logprob"]) for item in top}
