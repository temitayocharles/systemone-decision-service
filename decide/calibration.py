from __future__ import annotations

import json
import math
from typing import Dict, Iterable, List, Sequence, Tuple

import numpy as np

from . import config


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


def fit_temperature_binary(
    labels: Sequence[int], probs: Sequence[float]
) -> Tuple[float, float, float]:
    """Fit one temperature T minimizing binary NLL.

    p_T = sigmoid(logit(p) / T), logit(p) = log(p / (1 - p)).
    Returns (best_temperature, best_nll, ece_after_fit) where ECE is computed
    on confidence = max(p_T, 1 - p_T) against correctness.
    """
    labs = np.asarray(labels, dtype=float)
    p = np.clip(np.asarray(probs, dtype=float), 1e-6, 1.0 - 1e-6)
    logit = np.log(p / (1.0 - p))
    best_temp = 1.0
    best_nll = float("inf")
    best_ece = float("inf")
    for temp in np.linspace(0.2, 4.0, 80):
        p_t = 1.0 / (1.0 + np.exp(-logit / temp))
        p_t = np.clip(p_t, 1e-12, 1.0 - 1e-12)
        nll = float(-np.mean(labs * np.log(p_t) + (1.0 - labs) * np.log(1.0 - p_t)))
        conf = np.maximum(p_t, 1.0 - p_t)
        correct = ((p_t >= 0.5).astype(float) == labs).astype(int)
        ece = expected_calibration_error(conf, correct)
        if nll < best_nll:
            best_nll = nll
            best_temp = float(temp)
            best_ece = ece
    return best_temp, best_nll, best_ece


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


def fit_temperature_multiclass(
    labels: Sequence[int], logits: Sequence[Sequence[float]]
) -> Tuple[float, float, float]:
    """Fit one temperature T minimizing NLL over softmax(logits / T).

    labels: correct class index per example. logits: raw per-class logits.
    Returns (best_temperature, best_nll, ece_after_fit).
    """
    labs = np.asarray(labels, dtype=int)
    L = np.asarray(logits, dtype=float)
    best_temp = 1.0
    best_nll = float("inf")
    best_ece = float("inf")
    for temp in np.linspace(0.2, 4.0, 80):
        shifted = L / temp - np.max(L / temp, axis=1, keepdims=True)
        exps = np.exp(shifted)
        p = exps / np.sum(exps, axis=1, keepdims=True)
        nll = float(-np.mean(np.log(np.clip(p[np.arange(len(labs)), labs], 1e-12, 1.0))))
        ece = expected_calibration_error(np.max(p, axis=1), (np.argmax(p, axis=1) == labs).astype(int))
        if nll < best_nll:
            best_nll = nll
            best_temp = float(temp)
            best_ece = ece
    return best_temp, best_nll, best_ece


def save_temperatures(temperatures: Dict[str, float]) -> None:
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    tmp = config.TEMPERATURES_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps({k: float(v) for k, v in temperatures.items()}, indent=2))
    tmp.replace(config.TEMPERATURES_FILE)


def load_temperatures() -> Dict[str, float]:
    path = config.TEMPERATURES_FILE
    if not path.exists():
        return {"choice": 1.0, "score": 1.0, "noul": 1.0}
    try:
        data = json.loads(path.read_text())
        out = {"choice": 1.0, "score": 1.0, "noul": 1.0}
        for key in out:
            if key in data:
                out[key] = float(data[key])
        return out
    except (json.JSONDecodeError, ValueError, TypeError):
        return {"choice": 1.0, "score": 1.0, "noul": 1.0}
