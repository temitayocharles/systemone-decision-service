from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any, Dict, Iterable

from .calibration import (
    expected_calibration_error,
    fit_temperature_binary,
    fit_temperature_multiclass,
)
from .calibration_profiles import CalibrationProfile, CalibrationProfileStore


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

    if question_type in {"null", "noul"}:
        labels = [int(row["label"]) for row in rows]
        probs = [float(row["probability"]) for row in rows]
        before_conf = [max(p, 1.0 - p) for p in probs]
        before_correct = [int((p >= 0.5) == bool(label)) for p, label in zip(probs, labels)]
        ece_before = expected_calibration_error(before_conf, before_correct)
        temperature, _, ece_after = fit_temperature_binary(labels, probs)
    else:
        labels = [int(row["label_index"]) for row in rows]
        logits = [row["logits"] for row in rows]
        before_probs = []
        before_correct = []
        from .calibration import softmax
        for label, values in zip(labels, logits):
            p = softmax(values, 1.0)
            before_probs.append(float(max(p)))
            before_correct.append(int(int(p.argmax()) == label))
        ece_before = expected_calibration_error(before_probs, before_correct)
        temperature, _, ece_after = fit_temperature_multiclass(labels, logits)

    profile = CalibrationProfile(
        provider=provider,
        model=model,
        question_type="null" if question_type == "noul" else question_type,
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
