import asyncio

from decide.providers.base import ProviderResult
from decide.runtime import DecisionRuntime
from decide.selection import ModelStats, SelectionPolicy


class FakeProviders:
    def capability_profiles(self):
        return {}


class FakeBenchmarks:
    def load(self):
        return [
            ModelStats(
                provider="cloud",
                model="cloud-model",
                task_type="generic",
                samples=100,
                accuracy=0.9,
                ece=0.05,
                p95_latency_ms=100,
                failure_rate=0.0,
                run_id="run",
                dataset_sha256="a" * 64,
                created_at="2026-01-01T00:00:00Z",
            )
        ]


class FakeTelemetry:
    def read(self, limit=10000):
        return []


async def _result(provider_name, state, questions, *, model, request_id):
    return ProviderResult(
        provider=provider_name,
        model=model or f"{provider_name}-model",
        answers={},
        usage={},
        latency_ms=1,
    )


def _runtime():
    runtime = object.__new__(DecisionRuntime)
    runtime.default_provider = "local"
    runtime.providers = FakeProviders()
    runtime.benchmarks = FakeBenchmarks()
    runtime.telemetry = FakeTelemetry()
    runtime._invoke = _result
    return runtime


def test_default_route_reports_default_selection():
    result = asyncio.run(
        _runtime().decide(
            state="state",
            questions={"q": {"type": "null"}},
        )
    )
    assert result["route"]["selection"] == "default"
    assert result["route"]["provider"] == "local"


def test_explicit_route_reports_explicit_selection():
    result = asyncio.run(
        _runtime().decide(
            state="state",
            questions={"q": {"type": "null"}},
            provider="cloud",
        )
    )
    assert result["route"]["selection"] == "explicit"
    assert result["route"]["provider"] == "cloud"


def test_empirical_route_reports_empirical_selection(monkeypatch):
    monkeypatch.setattr(
        "decide.runtime.choose_model",
        lambda *args, **kwargs: ModelStats(
            provider="cloud",
            model="cloud-model",
            task_type="generic",
        ),
    )
    result = asyncio.run(
        _runtime().decide(
            state="state",
            questions={"q": {"type": "null"}},
            policy=SelectionPolicy(task_type="generic"),
        )
    )
    assert result["route"]["selection"] == "empirical"
    assert result["route"]["provider"] == "cloud"
    assert result["route"]["model"] == "cloud-model"
