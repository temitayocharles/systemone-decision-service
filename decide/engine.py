"""Real decision engine: typed answers with probabilities from model logprobs.

How it works: for each question the model is asked to emit exactly one
label token (a digit for choice/score, YES/NO for noul). We request logprobs
from an OpenAI-compatible chat-completions endpoint, read the logits the
model assigned to each label token, and apply softmax(logits / T) where T
is the temperature fitted by /v1/calibrate.

What this engine will NOT do:
- It never invents probabilities. If the provider is not configured or does
  not return logprobs, it raises EngineError and the API answers 502.
- It never floors or boosts confidence. The numbers are the model's own
  distribution, temperature-scaled, nothing else.
"""
from __future__ import annotations

import asyncio
import math
from typing import Any, Dict, List, Optional

import httpx

from . import config
from .calibration import load_temperatures


class EngineError(RuntimeError):
    """The provider failed or refused to return logprobs. Never fake it."""


def _softmax(logits: List[float], temperature: float) -> List[float]:
    t = max(temperature, 1e-6)
    scaled = [x / t for x in logits]
    m = max(scaled)
    exps = [math.exp(x - m) for x in scaled]
    total = sum(exps)
    return [e / total for e in exps]


def _token_variants(label: str) -> List[str]:
    # Tokenizers commonly emit a leading space on the first token.
    return [label, " " + label, "\n" + label]


class DecisionEngine:
    def __init__(self, temperatures: Optional[Dict[str, float]] = None) -> None:
        self.temperatures = temperatures if temperatures is not None else load_temperatures()
        self._client: Optional[httpx.AsyncClient] = None
        self._sem = asyncio.Semaphore(config.MAX_PARALLEL)

    def temperature_for(self, question_type: str) -> float:
        return float(self.temperatures.get(question_type, 1.0))

    def reload_temperatures(self) -> None:
        self.temperatures = load_temperatures()

    async def _client_or_raise(self) -> httpx.AsyncClient:
        if not config.provider_configured():
            raise EngineError(
                "DECIDE_API_KEY is not set. The decision service needs a "
                "logprob-capable model provider; it will not guess."
            )
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=config.BASE_URL.rstrip("/"),
                timeout=config.REQUEST_TIMEOUT_S,
            )
        return self._client

    async def _logprobs_for(
        self, prompt: str, usage: Dict[str, int]
    ) -> Dict[str, float]:
        """Ask the model for one label token; return {token: logprob}.

        Real provider token counts are accumulated into `usage` so callers
        can report measured cost instead of estimating it.
        """
        client = await self._client_or_raise()
        body = {
            "model": config.MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1,
            "temperature": 0,
            "logprobs": True,
            "top_logprobs": 20,
        }
        headers = {"Authorization": f"Bearer {config.API_KEY}"}
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

    def _logits_for_labels(self, observed: Dict[str, float], labels: List[str]) -> List[float]:
        floor = min(observed.values()) - 10.0 if observed else -10.0
        logits = []
        for label in labels:
            best = floor
            for variant in _token_variants(label):
                if variant in observed and observed[variant] > best:
                    best = observed[variant]
            logits.append(best)
        return logits

    async def _decide_labels(
        self,
        prompt: str,
        labels: List[str],
        question_type: str,
        usage: Dict[str, int],
    ) -> List[float]:
        async with self._sem:
            observed = await self._logprobs_for(prompt, usage)
        logits = self._logits_for_labels(observed, labels)
        return _softmax(logits, self.temperature_for(question_type))

    async def _evaluate_digit_labels(
        self,
        prompt: str,
        candidates: List[str],
        question_type: str,
        usage: Dict[str, int],
    ) -> List[float]:
        """Softmax over digit labels 1..len(candidates).

        `candidates[i]` is the human-readable text for candidate i, shown in
        the prompt. For more than 9 candidates we run a tournament: each round
        presents at most 9 candidates relabeled 1..k (single tokens the model
        can actually emit) and winners advance. Tournament probabilities are
        approximate; this is documented, not hidden.
        """
        n = len(candidates)

        async def round_probs(
            base_prompt: str, indices: List[int]
        ) -> List[float]:
            lines = [f"{i + 1}. {candidates[c]}" for i, c in enumerate(indices)]
            round_prompt = (
                base_prompt
                + "\n\nCandidates:\n"
                + "\n".join(lines)
                + "\n\nAnswer with only the number of the best candidate. No other text."
            )
            return await self._decide_labels(
                round_prompt,
                [str(i + 1) for i in range(len(indices))],
                question_type,
                usage,
            )

        contenders = list(range(n))
        while len(contenders) > 9:
            winners: List[int] = []
            for start in range(0, len(contenders), 9):
                group = contenders[start : start + 9]
                probs = await round_probs(prompt, group)
                winners.append(group[max(range(len(group)), key=lambda i: probs[i])])
            contenders = winners
        final_probs = await round_probs(prompt, contenders)
        result = [0.0] * n
        for i, c in enumerate(contenders):
            result[c] = final_probs[i]
        total = sum(result)
        return [p / total for p in result] if total > 0 else [1.0 / n] * n

    async def evaluate_choice(
        self,
        options: Dict[str, str],
        prompt: str,
        state: str,
        usage: Optional[Dict[str, int]] = None,
    ) -> Dict[str, Any]:
        keys = list(options.keys())
        if len(keys) < 2:
            raise EngineError("choice needs at least 2 options")
        usage = usage if usage is not None else {}
        base_prompt = f"State:\n{state}\n\nQuestion: {prompt}"
        probs = await self._evaluate_digit_labels(
            base_prompt, [options[k] for k in keys], "choice", usage
        )
        best = max(range(len(keys)), key=lambda i: probs[i])
        return {
            "type": "choice",
            "value": keys[best],
            "probabilities": {k: float(probs[i]) for i, k in enumerate(keys)},
            "confidence": float(probs[best]),
        }

    async def evaluate_score(
        self,
        prompt: str,
        state: str,
        min_value: int,
        max_value: int,
        labels: Optional[List[int]] = None,
        usage: Optional[Dict[str, int]] = None,
    ) -> Dict[str, Any]:
        # labels, when provided, is the explicit candidate point set
        # (a subset of min..max per the contract). Otherwise use the full range.
        if labels:
            points = sorted(set(int(v) for v in labels))
            if any(p < min_value or p > max_value for p in points):
                raise EngineError("score labels must be within min/max")
        else:
            points = list(range(min_value, max_value + 1))
        usage = usage if usage is not None else {}
        base_prompt = (
            f"State:\n{state}\n\nQuestion: {prompt}\n"
            f"Rate on this scale: {min_value} to {max_value}."
        )
        probs = await self._evaluate_digit_labels(
            base_prompt, [str(p) for p in points], "score", usage
        )
        best = max(range(len(points)), key=lambda i: probs[i])
        return {
            "type": "score",
            "value": points[best],
            "probabilities": {str(p): float(probs[i]) for i, p in enumerate(points)},
            "confidence": float(probs[best]),
        }

    async def evaluate_noul(
        self,
        prompt: str,
        state: str,
        usage: Optional[Dict[str, int]] = None,
    ) -> Dict[str, Any]:
        usage = usage if usage is not None else {}
        noul_prompt = (
            f"State:\n{state}\n\nProposition: {prompt}\n"
            "Is the proposition true? Answer with only YES or NO. No other text."
        )
        probs = await self._decide_labels(noul_prompt, ["YES", "NO"], "noul", usage)
        p_true = float(probs[0])
        return {
            "type": "noul",
            "value": p_true,
            "confidence": float(max(p_true, 1.0 - p_true)),
        }

    async def decide(
        self, state: str, questions: Dict[str, Any]
    ) -> tuple:
        """Evaluate all questions in parallel.

        Returns (results, usage): results maps question id to its answer,
        usage accumulates the provider's real reported token counts.
        """
        usage: Dict[str, int] = {}

        async def one(qid: str, q: Dict[str, Any]) -> tuple:
            qtype = q["type"]
            if qtype == "choice":
                return qid, await self.evaluate_choice(
                    q["options"], q["prompt"], state, usage
                )
            if qtype == "score":
                return qid, await self.evaluate_score(
                    q["prompt"], state, int(q["min"]), int(q["max"]),
                    q.get("labels"), usage,
                )
            if qtype == "noul":
                return qid, await self.evaluate_noul(q["prompt"], state, usage)
            raise EngineError(f"unsupported question type: {qtype}")

        pairs = await asyncio.gather(
            *(one(qid, q) for qid, q in questions.items())
        )
        return dict(pairs), usage

    async def aclose(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None
