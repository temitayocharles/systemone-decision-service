from decide.providers.base import ProviderResult
from decide.runtime import _merge_results


def test_ensemble_choice_probabilities_are_averaged():
    left = ProviderResult(
        provider="a",
        model="m1",
        answers={
            "route": {
                "type": "choice",
                "value": "x",
                "probabilities": {"x": 0.8, "y": 0.2},
                "confidence": 0.8,
            }
        },
        usage={"total_tokens": 10},
        latency_ms=20,
    )
    right = ProviderResult(
        provider="b",
        model="m2",
        answers={
            "route": {
                "type": "choice",
                "value": "y",
                "probabilities": {"x": 0.4, "y": 0.6},
                "confidence": 0.6,
            }
        },
        usage={"total_tokens": 20},
        latency_ms=30,
    )
    merged = _merge_results([left, right])
    assert merged["answers"]["route"]["value"] == "x"
    assert round(merged["answers"]["route"]["probabilities"]["x"], 3) == 0.6
    assert merged["usage"]["total_tokens"] == 30
    assert merged["latency_ms"] == 30
