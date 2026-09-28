from __future__ import annotations

import math
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any, Dict, Iterable

from .calibration import (
    expected_calibration_error,
    fit_temperature_binary,
    fit_temperature_multiclass,
    softmax,
)
from .calibration_profiles import CalibrationProfile, CalibrationProfileStore


def _probabilities_to_logits(probabilities: Iterable[float]) -> list[float]:
    probs = [max(float(p), 1e-12) for p in probabilities]
    total = sum(probs)
    if total <= 0:
        raise ValueError("probabilities must contain positive mass")
    return [math.log(p / total) for p in probs]


def fit_profile(
    *,
    provider: str,
    model: str,
    question_type: str,
    examples: Iterable[Dict[str, Any]],
    version: str | None = None,
) -> CalibrationProfile:
    rows = list(examples)
    if len(rows) < 20:
        raise ValueError("at least 20 labelled calibration examples are required")

    normalized_type = "null" if question_type == "noul" else question_type
    if normalized_type == "null":
        labels = [int(row["label"]) for row in rows]
        probs = [float(row["probability"]) for row in rows]
        before_conf = [max(p, 1.0 - p) for p in probs]
        before_correct = [
            int((p >= 0.5) == bool(label))
            for p, label in zip(probs, labels)
        ]
        ece_before = expected_calibration_error(before_conf, before_correct)
        temperature, _, ece_after = fit_temperature_binary(labels, probs)
    elif normalized_type in {"choice", "score"}:
        labels = [int(row["label_index"]) for row in rows]
        logits = []
        before_conf = []
        before_correct = []
        for label, row in zip(labels, rows):
            values = row.get("logits")
            if values is None:
                values = _probabilities_to_logits(row["probabilities"])
            values = [float(v) for v in values]
            logits.append(values)
            p = softmax(values, 1.0)
            before_conf.append(float(max(p)))
            before_correct.append(int(int(p.argmax()) == label))
        ece_before = expected_calibration_error(before_conf, before_correct)
        temperature, _, ece_after = fit_temperature_multiclass(labels, logits)
    else:
        raise ValueError(f"unsupported question_type: {question_type}")

    profile = CalibrationProfile(
        provider=provider,
        model=model,
        question_type=normalized_type,
        version=version or datetime.now(timezone.utc).isoformat(),
        temperature=float(temperature),
        samples=len(rows),
        ece_before=float(ece_before),
        ece_after=float(ece_after),
    )
    CalibrationProfileStore().upsert(profile)
    return profile


def profile_dict(profile: CalibrationProfile) -> Dict[str, Any]:
    return asdict(profile)
