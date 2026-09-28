from decide.capabilities import CapabilityProfile
from decide.health import latest_health
from decide.selection import ModelStats, SelectionPolicy, choose_model


def _stats(provider, accuracy=0.90, ece=0.03):
    return ModelStats(
        provider=provider,
        model=f"{provider}-model",
        task_type="routing",
        samples=100,
        accuracy=accuracy,
        ece=ece,
        p95_latency_ms=100,
        failure_rate=0.0,
    )


def test_capabilities_filter_before_empirical_scoring():
    candidates = [_stats("cloud", 0.98), _stats("private", 0.91)]
    capabilities = {
        "cloud": CapabilityProfile("cloud", {"token_logprobs"}, {"local": False}),
        "private": CapabilityProfile(
            "private", {"token_logprobs", "private_runtime"}, {"local": True}
        ),
    }
    selected = choose_model(
        candidates,
        SelectionPolicy(
            task_type="routing",
            required_capabilities=["private_runtime"],
            attribute_equals={"local": True},
        ),
        capabilities=capabilities,
        health={"cloud": True, "private": True},
    )
    assert selected.provider == "private"


def test_unhealthy_provider_is_excluded_by_default():
    selected = choose_model(
        [_stats("a", 0.99), _stats("b", 0.90)],
        SelectionPolicy(task_type="routing"),
        health={"a": False, "b": True},
    )
    assert selected.provider == "b"


def test_unknown_health_is_not_treated_as_failure():
    selected = choose_model(
        [_stats("a", 0.95)],
        SelectionPolicy(task_type="routing"),
        health={},
    )
    assert selected.provider == "a"


def test_latest_health_uses_latest_observation():
    health = latest_health([
        {"ts": 1, "provider": "x", "status": "error"},
        {"ts": 2, "provider": "x", "status": "ok"},
        {"ts": 1, "provider": "y", "status": "error"},
    ])
    assert health == {"x": True, "y": False}
