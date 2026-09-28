"""Decision-engine probability and fail-closed unit tests.

Provider I/O is mocked. Live runtime certification is handled by
scripts/certify_runtime.py against the configured System One service.
"""
import asyncio

import pytest

from decide import config
from decide.engine import DecisionEngine, EngineError


def make_fake(logprob_map):
    async def fake(self, prompt: str, usage=None):
        return dict(logprob_map)
    return fake


def run(coro):
    return asyncio.run(coro)


def test_choice_picks_highest_logit_and_sums_to_one(monkeypatch):
    monkeypatch.setattr(
        DecisionEngine,
        "_logprobs_for",
        make_fake({"1": -0.1, "2": -2.3, "3": -3.0, "4": -4.1}),
    )
    eng = DecisionEngine(
        temperatures={"choice": 1.0, "score": 1.0, "null": 1.0}
    )
    ans = run(
        eng.evaluate_choice(
            {"a": "first", "b": "second", "c": "third"},
            "pick",
            "state",
        )
    )
    assert ans["type"] == "choice"
    assert ans["value"] == "a"
    assert abs(sum(ans["probabilities"].values()) - 1.0) < 1e-9
    assert ans["confidence"] == pytest.approx(ans["probabilities"]["a"])
    assert (
        ans["probabilities"]["a"]
        > ans["probabilities"]["b"]
        > ans["probabilities"]["c"]
    )
    run(eng.aclose())


def test_choice_handles_leading_space_tokens(monkeypatch):
    monkeypatch.setattr(
        DecisionEngine,
        "_logprobs_for",
        make_fake({" 1": -3.0, " 2": -0.2, "YES": -9.0}),
    )
    eng = DecisionEngine(
        temperatures={"choice": 1.0, "score": 1.0, "null": 1.0}
    )
    ans = run(
        eng.evaluate_choice(
            {"a": "first", "b": "second"},
            "pick",
            "state",
        )
    )
    assert ans["value"] == "b"
    run(eng.aclose())


def test_temperature_scaling_changes_distribution(monkeypatch):
    async def fake(self, prompt: str, usage=None):
        return {"1": 0.0, "2": -1.0}

    monkeypatch.setattr(DecisionEngine, "_logprobs_for", fake)
    cold = DecisionEngine(
        temperatures={"choice": 0.2, "score": 1.0, "null": 1.0}
    )
    hot = DecisionEngine(
        temperatures={"choice": 5.0, "score": 1.0, "null": 1.0}
    )
    a_cold = run(
        cold.evaluate_choice({"a": "x", "b": "y"}, "pick", "state")
    )
    a_hot = run(
        hot.evaluate_choice({"a": "x", "b": "y"}, "pick", "state")
    )
    assert a_cold["probabilities"]["a"] > a_hot["probabilities"]["a"] > 0.5
    run(cold.aclose())
    run(hot.aclose())


def test_null_returns_probability_of_yes(monkeypatch):
    monkeypatch.setattr(
        DecisionEngine,
        "_logprobs_for",
        make_fake({"YES": -0.4, "NO": -1.2}),
    )
    eng = DecisionEngine(
        temperatures={"choice": 1.0, "score": 1.0, "null": 1.0}
    )
    ans = run(eng.evaluate_noul("is it true?", "state"))
    assert ans["type"] == "null"
    assert 0.5 < ans["value"] < 1.0
    assert ans["confidence"] == pytest.approx(ans["value"])
    run(eng.aclose())


def test_score_picks_best_point(monkeypatch):
    monkeypatch.setattr(
        DecisionEngine,
        "_logprobs_for",
        make_fake({"1": -4.0, "2": -3.0, "3": -2.0, "4": -0.5, "5": -1.5}),
    )
    eng = DecisionEngine(
        temperatures={"choice": 1.0, "score": 1.0, "null": 1.0}
    )
    ans = run(eng.evaluate_score("rate it", "state", 1, 5))
    assert ans["value"] == 4
    assert abs(sum(ans["probabilities"].values()) - 1.0) < 1e-9
    run(eng.aclose())


def test_unconfigured_legacy_engine_fails_closed(monkeypatch):
    monkeypatch.setattr(config, "API_KEY", "")
    eng = DecisionEngine()
    with pytest.raises(EngineError):
        run(eng._logprobs_for("hi", {}))
    run(eng.aclose())
