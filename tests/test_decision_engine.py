"""Engine and API contract tests with a MOCKED model provider.

Nothing here calls a real model. DecisionEngine._logprobs_for is replaced with
a fake that returns fixed logprobs, so these tests verify the honest plumbing:
label extraction, softmax, temperature scaling, error propagation, and the
HTTP contract. A live-provider test exists but is skipped without DECIDE_API_KEY.
"""
import asyncio
import os

import pytest
from fastapi.testclient import TestClient

from decide import config
from decide.app import app
from decide.engine import DecisionEngine, EngineError


def make_fake(logprob_map):
    async def fake(self, prompt: str, usage=None):
        return dict(logprob_map)

    return fake


@pytest.fixture()
def engine(monkeypatch):
    monkeypatch.setattr(
        DecisionEngine,
        "_logprobs_for",
        make_fake({"1": -0.1, "2": -2.3, "3": -3.0, "4": -4.1}),
    )
    eng = DecisionEngine(temperatures={"choice": 1.0, "score": 1.0, "noul": 1.0})
    yield eng
    asyncio.get_event_loop().run_until_complete(eng.aclose())


def test_choice_picks_highest_logit_and_sums_to_one(engine):
    options = {"a": "first", "b": "second", "c": "third"}
    ans = asyncio.get_event_loop().run_until_complete(
        engine.evaluate_choice(options, "pick", "state")
    )
    assert ans["type"] == "choice"
    assert ans["value"] == "a"
    assert abs(sum(ans["probabilities"].values()) - 1.0) < 1e-9
    assert ans["confidence"] == pytest.approx(ans["probabilities"]["a"])
    assert ans["probabilities"]["a"] > ans["probabilities"]["b"] > ans["probabilities"]["c"]


def test_choice_handles_leading_space_tokens(monkeypatch):
    monkeypatch.setattr(
        DecisionEngine,
        "_logprobs_for",
        make_fake({" 1": -3.0, " 2": -0.2, "YES": -9.0}),
    )
    eng = DecisionEngine(temperatures={"choice": 1.0, "score": 1.0, "noul": 1.0})
    ans = asyncio.get_event_loop().run_until_complete(
        eng.evaluate_choice({"a": "first", "b": "second"}, "pick", "state")
    )
    assert ans["value"] == "b"
    asyncio.get_event_loop().run_until_complete(eng.aclose())


def test_temperature_scaling_changes_distribution(monkeypatch):
    async def fake(self, prompt: str, usage=None):
        return {"1": 0.0, "2": -1.0}

    monkeypatch.setattr(DecisionEngine, "_logprobs_for", fake)
    cold = DecisionEngine(temperatures={"choice": 0.2, "score": 1.0, "noul": 1.0})
    hot = DecisionEngine(temperatures={"choice": 5.0, "score": 1.0, "noul": 1.0})
    loop = asyncio.get_event_loop()
    a_cold = loop.run_until_complete(
        cold.evaluate_choice({"a": "x", "b": "y"}, "pick", "state")
    )
    a_hot = loop.run_until_complete(
        hot.evaluate_choice({"a": "x", "b": "y"}, "pick", "state")
    )
    assert a_cold["probabilities"]["a"] > a_hot["probabilities"]["a"] > 0.5
    loop.run_until_complete(cold.aclose())
    loop.run_until_complete(hot.aclose())


def test_noul_returns_probability_of_yes(monkeypatch):
    monkeypatch.setattr(
        DecisionEngine, "_logprobs_for", make_fake({"YES": -0.4, "NO": -1.2})
    )
    eng = DecisionEngine(temperatures={"choice": 1.0, "score": 1.0, "noul": 1.0})
    ans = asyncio.get_event_loop().run_until_complete(
        eng.evaluate_noul("is it true?", "state")
    )
    assert ans["type"] == "noul"
    assert 0.5 < ans["value"] < 1.0
    assert ans["confidence"] == pytest.approx(ans["value"])
    asyncio.get_event_loop().run_until_complete(eng.aclose())


def test_score_picks_best_point(monkeypatch):
    monkeypatch.setattr(
        DecisionEngine,
        "_logprobs_for",
        make_fake({"1": -4.0, "2": -3.0, "3": -2.0, "4": -0.5, "5": -1.5}),
    )
    eng = DecisionEngine(temperatures={"choice": 1.0, "score": 1.0, "noul": 1.0})
    ans = asyncio.get_event_loop().run_until_complete(
        eng.evaluate_score("rate it", "state", 1, 5)
    )
    assert ans["value"] == 4
    assert abs(sum(ans["probabilities"].values()) - 1.0) < 1e-9
    asyncio.get_event_loop().run_until_complete(eng.aclose())


def test_missing_api_key_raises_engine_error(monkeypatch):
    monkeypatch.setattr(config, "API_KEY", "")
    eng = DecisionEngine()
    with pytest.raises(EngineError, match="DECIDE_API_KEY"):
        asyncio.get_event_loop().run_until_complete(eng._logprobs_for("hi", {}))
    asyncio.get_event_loop().run_until_complete(eng.aclose())


@pytest.fixture()
def client(monkeypatch):
    monkeypatch.setattr(config, "API_KEY", "test-key")
    monkeypatch.setattr(
        DecisionEngine,
        "_logprobs_for",
        make_fake({"1": -0.2, "2": -1.8, "YES": -0.3, "NO": -1.5}),
    )
    with TestClient(app) as c:
        yield c


def test_decide_contract_shape(client):
    resp = client.post(
        "/v1/decide",
        json={
            "state": "the payment service is down",
            "questions": {
                "need": {
                    "type": "choice",
                    "prompt": "what is needed?",
                    "options": {"fix": "fix it", "wait": "wait it out"},
                },
                "urgent": {"type": "noul", "prompt": "is this urgent?"},
            },
        },
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert set(body["results"]) == {"need", "urgent"}
    assert body["results"]["need"]["value"] == "fix"
    assert body["results"]["urgent"]["type"] == "noul"
    assert "meta" in body
    assert body["meta"]["model"] == config.MODEL
    assert "temperatures" in body["meta"]
    assert set(body["meta"]["usage"]) == {
        "prompt_tokens",
        "completion_tokens",
        "total_tokens",
    }


def test_decide_rejects_empty_prompt(client):
    resp = client.post(
        "/v1/decide",
        json={
            "state": "x",
            "questions": {
                "q": {"type": "noul", "prompt": "   "},
            },
        },
    )
    assert resp.status_code == 422


def test_decide_without_api_key_is_502_not_a_guess(monkeypatch):
    monkeypatch.setattr(config, "API_KEY", "")
    with TestClient(app) as c:
        resp = c.post(
            "/v1/decide",
            json={
                "state": "x",
                "questions": {"q": {"type": "noul", "prompt": "is it true?"}},
            },
        )
    assert resp.status_code == 502
    assert "DECIDE_API_KEY" in resp.json()["detail"]


def test_health_reports_provider_status():
    with TestClient(app) as c:
        resp = c.get("/v1/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
    assert "provider_configured" in resp.json()


@pytest.mark.skipif(
    not os.getenv("DECIDE_API_KEY"),
    reason="live provider test: needs DECIDE_API_KEY",
)
def test_live_provider_smoke():
    """Hits the real provider once. Skipped in CI; run manually with a key."""
    eng = DecisionEngine()
    ans = asyncio.get_event_loop().run_until_complete(
        eng.evaluate_noul("the sky is blue", "general knowledge")
    )
    assert ans["value"] > 0.5
    asyncio.get_event_loop().run_until_complete(eng.aclose())
