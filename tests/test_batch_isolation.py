import asyncio

from decide.runtime import DecisionRuntime


def test_batch_returns_item_errors_without_failing_whole_batch(monkeypatch):
    runtime = DecisionRuntime()

    async def fake_decide(**kwargs):
        if kwargs["state"] == "bad":
            raise RuntimeError("boom")
        return {"answers": {}, "route": {}, "usage": {}, "latency_ms": 1}

    monkeypatch.setattr(runtime, "decide", fake_decide)

    results = asyncio.run(runtime.batch([
        {"state": "good", "questions": {"q": {"type": "null"}}},
        {"state": "bad", "questions": {"q": {"type": "null"}}},
    ]))

    assert results[0]["ok"] is True
    assert results[1]["ok"] is False
    assert results[1]["error"]["type"] == "RuntimeError"
