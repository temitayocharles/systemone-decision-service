"""Deterministic unit tests for the calibration math.

No model provider is involved here. These tests pin down the properties the
whole service depends on: softmax is a distribution, ECE measures what it
claims, and temperature fitting actually minimizes NLL on synthetic data
generated from a known temperature.
"""
import math

import numpy as np
import pytest

from decide import config
from decide.calibration import (
    expected_calibration_error,
    fit_temperature_binary,
    fit_temperature_multiclass,
    load_temperatures,
    save_temperatures,
    softmax,
)


def test_softmax_is_a_distribution():
    p = softmax([2.0, 1.0, 0.1])
    assert abs(sum(p) - 1.0) < 1e-9
    assert all(0.0 <= v <= 1.0 for v in p)
    # argmax preserved
    assert int(np.argmax(p)) == 0


def test_softmax_temperature_sharpens_and_flattens():
    logits = [3.0, 1.0, 0.0]
    cold = softmax(logits, temperature=0.2)
    hot = softmax(logits, temperature=5.0)
    assert cold[0] > softmax(logits, temperature=1.0)[0] > hot[0]
    # hot is closer to uniform
    assert max(hot) - min(hot) < max(cold) - min(cold)


def test_ece_perfect_predictions_is_zero():
    probs = [0.9, 0.1, 0.8, 0.2, 0.7, 0.3]
    labels = [1, 0, 1, 0, 1, 0]
    assert expected_calibration_error(probs, labels) < 0.35


def test_ece_confident_and_wrong_is_high():
    probs = [0.99] * 50 + [0.01] * 50
    labels = [0] * 50 + [1] * 50
    assert expected_calibration_error(probs, labels) > 0.8


def test_ece_well_calibrated_is_low():
    rng = np.random.default_rng(0)
    probs, labels = [], []
    for _ in range(2000):
        p = rng.uniform(0.05, 0.95)
        probs.append(p)
        labels.append(int(rng.random() < p))
    assert expected_calibration_error(probs, labels, bins=10) < 0.05


def _synthetic_binary(n=600, true_temp=2.0, seed=1):
    rng = np.random.default_rng(seed)
    logits = rng.normal(0, 2.0, size=n)
    p_true = 1.0 / (1.0 + np.exp(-logits / true_temp))
    labels = (rng.random(n) < p_true).astype(int)
    # what the model reports at T=1
    p_reported = 1.0 / (1.0 + np.exp(-logits))
    return labels, p_reported


def test_fit_temperature_binary_recovers_true_temperature():
    labels, probs = _synthetic_binary()
    temp, nll, ece_after = fit_temperature_binary(labels, probs)
    assert abs(temp - 2.0) < 0.35, f"fitted {temp}, expected ~2.0"
    # fitted NLL must beat no scaling
    p = np.clip(np.asarray(probs), 1e-12, 1 - 1e-12)
    nll_1 = float(-np.mean(labels * np.log(p) + (1 - labels) * np.log(1 - p)))
    assert nll <= nll_1 + 1e-9


def _synthetic_multiclass(n=600, true_temp=0.5, seed=2):
    rng = np.random.default_rng(seed)
    logits = rng.normal(0, 1.5, size=(n, 4))
    scaled = logits / true_temp
    scaled -= scaled.max(axis=1, keepdims=True)
    exps = np.exp(scaled)
    p_true = exps / exps.sum(axis=1, keepdims=True)
    labels = np.array([rng.choice(4, p=p_true[i]) for i in range(n)])
    # model reports at T=1
    s1 = logits - logits.max(axis=1, keepdims=True)
    e1 = np.exp(s1)
    p_reported = e1 / e1.sum(axis=1, keepdims=True)
    return labels, p_reported


def test_fit_temperature_multiclass_recovers_true_temperature():
    labels, p_reported = _synthetic_multiclass()
    logits = [[math.log(max(p, 1e-12)) for p in row] for row in p_reported]
    temp, nll, ece_after = fit_temperature_multiclass(labels, logits)
    assert abs(temp - 0.5) < 0.25, f"fitted {temp}, expected ~0.5"


def test_save_and_load_temperatures_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DATA_DIR", tmp_path)
    monkeypatch.setattr(config, "TEMPERATURES_FILE", tmp_path / "temperatures.json")
    save_temperatures({"choice": 1.7, "score": 0.6, "noul": 2.2})
    loaded = load_temperatures()
    assert loaded == {"choice": 1.7, "score": 0.6, "noul": 2.2}


def test_load_temperatures_defaults_when_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DATA_DIR", tmp_path)
    monkeypatch.setattr(config, "TEMPERATURES_FILE", tmp_path / "temperatures.json")
    assert load_temperatures() == {"choice": 1.0, "score": 1.0, "noul": 1.0}
