from __future__ import annotations

import math
from typing import Dict, Iterable, List, Sequence, Tuple

import numpy as np


def softmax(logits: Sequence[float], temperature: float = 1.0) -> np.ndarray:
    scaled = np.asarray(logits, dtype=float) / max(temperature, 1e-8)
    shifted = scaled - np.max(scaled)
    exps = np.exp(shifted)
    total = np.sum(exps)
    if total == 0:
        return np.full_like(exps, 1.0 / len(exps), dtype=float)
    return exps / total


def expected_calibration_error(probabilities: Sequence[float], labels: Sequence[int], bins: int = 10) -> float:
    probs = np.asarray(probabilities, dtype=float)
    labs = np.asarray(labels, dtype=float)
    bin_edges = np.linspace(0.0, 1.0, bins + 1)
    ece = 0.0
    total = len(labs)
    for i in range(bins):
        lo = bin_edges[i]
        hi = bin_edges[i + 1]
        mask = (probs >= lo) & (probs < hi if i < bins - 1 else probs <= hi)
        if not np.any(mask):
            continue
        avg_conf = float(np.mean(probs[mask]))
        avg_acc = float(np.mean(labs[mask]))
        ece += (np.sum(mask) / total) * abs(avg_acc - avg_conf)
    return float(ece)


def fit_temperature_for_binary(labels: Sequence[int], probs: Sequence[float]) -> Tuple[float, float, float]:
    best_temp = 1.0
    best_nll = float("inf")
    best_after = 1.0
    for temp in np.linspace(0.2, 4.0, 80):
        p = softmax(np.log(np.clip(np.asarray(probs, dtype=float), 1e-6, 1.0)), temperature=temp)
        nll = -np.mean(np.log(np.clip(p, 1e-12, 1.0)))
        if nll < best_nll:
            best_nll = nll
            best_temp = float(temp)
            best_after = float(expected_calibration_error(np.clip(p, 0.0, 1.0), labels))
    return best_temp, float(best_nll), best_after


def reliability_diagram(probabilities: Sequence[float], labels: Sequence[int], bins: int = 10) -> Dict[str, List[float]]:
    probs = np.asarray(probabilities, dtype=float)
    labs = np.asarray(labels, dtype=float)
    edges = np.linspace(0.0, 1.0, bins + 1)
    buckets = []
    for i in range(bins):
        lo = edges[i]
        hi = edges[i + 1]
        if i == bins - 1:
            mask = (probs >= lo) & (probs <= hi)
        else:
            mask = (probs >= lo) & (probs < hi)
        if not np.any(mask):
            buckets.append({"bin": [lo, hi], "count": 0, "avg_conf": 0.0, "avg_acc": 0.0})
        else:
            buckets.append({
                "bin": [lo, hi],
                "count": int(np.sum(mask)),
                "avg_conf": float(np.mean(probs[mask])),
                "avg_acc": float(np.mean(labs[mask]))
            })
    return {"bins": buckets}
