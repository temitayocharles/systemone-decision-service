from __future__ import annotations

import asyncio
from typing import Dict, List

from .engine import DecisionEngine, EngineError


class ScalableDecisionEngine(DecisionEngine):
    """Decision engine without the old >9 candidate tournament approximation.

    For >9 candidates, score every candidate independently as YES/NO against the
    same state/question, then normalize all P(YES) values into one distribution.
    This costs more provider calls, but no candidate is silently eliminated.
    """

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
