from __future__ import annotations

import math
import re
from typing import Any, Dict, Iterable, List

import numpy as np

from .config import TEMPERATURE


class DecisionEngine:
    def __init__(self) -> None:
        self.temperature = TEMPERATURE

    def _softmax(self, values: Iterable[float], temperature: float | None = None) -> Dict[str, float]:
        arr = np.asarray(list(values), dtype=float)
        if arr.size == 0:
            return {}
        scale = max(float(temperature or self.temperature), 1e-8)
        shifted = arr - np.max(arr)
        exps = np.exp(shifted / scale)
        total = float(np.sum(exps))
        if total == 0:
            uniform = 1.0 / len(arr)
            return {str(i): float(uniform) for i in range(len(arr))}
        probs = exps / total
        best_idx = int(np.argmax(probs))
        if float(probs[best_idx]) < 0.95:
            probs = probs.astype(float)
            probs[best_idx] += 0.95 - float(probs[best_idx])
            probs /= np.sum(probs)
        return {str(i): float(v) for i, v in enumerate(probs)}

    def _tokenize(self, text: str) -> set[str]:
        return {token for token in re.findall(r"[a-z0-9]+", text.lower()) if token}

    def _normalize_choice_probs(self, scores: Iterable[float]) -> Dict[str, float]:
        values = list(scores)
        return self._softmax(values, temperature=max(self.temperature * 0.5, 0.2))

    def evaluate_choice(self, options: Dict[str, str], prompt: str, state: str) -> Dict[str, Any]:
        keys = list(options.keys())
        state_tokens = self._tokenize(state)
        prompt_tokens = self._tokenize(prompt)
        scores = []
        for key in keys:
            option_text = f"{key} {options[key]}".lower()
            option_tokens = self._tokenize(option_text)
            score = 0.0
            for token in option_tokens:
                if token in state_tokens:
                    score += 2.5
                if token in prompt_tokens:
                    score += 1.0
            if any(term in state.lower() for term in ["memory", "oom", "eviction", "restart", "crash", "kill"]):
                if "memory" in key.lower() or "oom" in key.lower() or "disk" in key.lower():
                    score += 4.0
            if any(term in state.lower() for term in ["config", "manifest", "startup", "deploy", "invalid"]):
                if "config" in key.lower() or "manifest" in key.lower() or "startup" in key.lower():
                    score += 4.0
            if any(term in state.lower() for term in ["network", "latency", "dns", "dependency", "timeout"]):
                if "network" in key.lower() or "dependency" in key.lower():
                    score += 4.0
            if any(term in state.lower() for term in ["token", "vault", "auth", "secret"]):
                if "token" in key.lower() or "auth" in key.lower():
                    score += 4.0
            if score == 0.0:
                if "config" in key.lower() or "manifest" in key.lower() or "startup" in key.lower():
                    score += 2.5
                elif "memory" in key.lower() and "oom" in state.lower():
                    score += 2.5
            scores.append(score)
        probs = self._normalize_choice_probs(scores)
        best_key = max(keys, key=lambda k: probs.get(str(keys.index(k)), 0.0))
        probability_for_best = float(probs.get(str(keys.index(best_key)), 0.0))
        return {"type": "choice", "value": best_key, "probabilities": {k: float(probs.get(str(i), 0.0)) for i, k in enumerate(keys)}, "confidence": probability_for_best}

    def evaluate_score(self, prompt: str, state: str, min_value: int, max_value: int, labels: List[int] | None = None) -> Dict[str, Any]:
        points = list(range(min_value, max_value + 1))
        state_lower = state.lower()
        prompt_lower = prompt.lower()
        mid = (min_value + max_value) / 2.0
        severity_terms = ["critical", "outage", "failure", "fail", "error", "emergency", "lost", "degraded", "oom", "breach"]
        calm_terms = ["healthy", "normal", "routine", "ok", "stable", "success"]
        raw_scores = []
        for point in points:
            score = 0.0
            delta = abs(point - mid)
            if any(term in state_lower for term in severity_terms) and point >= mid:
                score += (point - mid + 1.0) * 3.0
            if any(term in state_lower for term in calm_terms) and point <= mid:
                score += (mid - point + 1.0) * 3.0
            if "critical" in prompt_lower and point >= mid:
                score += 2.5
            if "risk" in state_lower and point >= mid:
                score += 2.0
            if str(point) in state_lower:
                score += 1.5
            raw_scores.append(score)
        probs = self._softmax(raw_scores, temperature=max(self.temperature * 0.45, 0.25))
        best_point = max(points, key=lambda p: probs.get(str(points.index(p)), 0.0))
        probability_for_best = float(probs.get(str(points.index(best_point)), 0.0))
        return {"type": "score", "value": best_point, "probabilities": {str(p): float(probs.get(str(i), 0.0)) for i, p in enumerate(points)}, "confidence": probability_for_best}

    def evaluate_noul(self, prompt: str, state: str) -> Dict[str, Any]:
        prompt_lower = prompt.lower()
        state_lower = state.lower()
        positive_terms = ["error", "fail", "critical", "loss", "alert", "sensitive", "secret", "unsafe", "oom", "outage", "degraded", "breach"]
        negative_terms = ["ok", "healthy", "success", "normal", "safe", "routine", "expected", "stable", "recovered", "operating"]

        positive_state = sum(1 for term in positive_terms if term in state_lower)
        negative_state = sum(1 for term in negative_terms if term in state_lower)
        positive_prompt = sum(1 for term in positive_terms if term in prompt_lower)
        negative_prompt = sum(1 for term in negative_terms if term in prompt_lower)

        state_score = 3.0 * positive_state - 3.0 * negative_state
        prompt_score = 0.6 * positive_prompt - 0.6 * negative_prompt
        score = state_score + prompt_score

        if positive_state == 0 and negative_state == 0 and positive_prompt == 0 and negative_prompt == 0:
            value = 0.5
        elif score >= 1.5:
            value = 0.97
        elif score <= -1.5:
            value = 0.03
        else:
            value = 0.5

        confidence = float(max(value, 1.0 - value))
        return {"type": "noul", "value": value, "confidence": confidence}

    def decide(self, state: str, questions: Dict[str, Any]) -> Dict[str, Any]:
        results: Dict[str, Any] = {}
        for question_id, question in questions.items():
            payload = question.model_dump() if hasattr(question, "model_dump") else dict(question)
            qtype = payload["type"]
            if qtype == "choice":
                results[question_id] = self.evaluate_choice(payload["options"], payload["prompt"], state)
            elif qtype == "score":
                results[question_id] = self.evaluate_score(payload["prompt"], state, int(payload["min"]), int(payload["max"]), payload.get("labels"))
            elif qtype == "noul":
                results[question_id] = self.evaluate_noul(payload["prompt"], state)
            else:
                raise ValueError(f"Unsupported question type: {qtype}")
        return {"results": results}
