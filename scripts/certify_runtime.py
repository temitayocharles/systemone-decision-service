from __future__ import annotations

import argparse
import json
import math
from typing import Any, Dict

import httpx


def _assert_probability(value: Any, name: str) -> float:
    p = float(value)
    if not 0.0 <= p <= 1.0:
        raise AssertionError(f"{name} must be in [0, 1], got {p}")
    return p


def validate_response(payload: Dict[str, Any]) -> None:
    route = payload.get("route") or {}
    if not route.get("provider"):
        raise AssertionError("response route is missing provider")
    if not route.get("model"):
        raise AssertionError("response route is missing model")

    answers = payload.get("answers") or {}
    choice = answers.get("choice")
    binary = answers.get("binary")
    if not choice or not binary:
        raise AssertionError("response is missing certification answers")

    probabilities = choice.get("probabilities") or {}
    if len(probabilities) != 2:
        raise AssertionError("choice answer must contain two probabilities")
    total = sum(float(v) for v in probabilities.values())
    if not math.isclose(total, 1.0, rel_tol=1e-5, abs_tol=1e-5):
        raise AssertionError(f"choice probabilities sum to {total}, not 1")

    _assert_probability(choice.get("confidence"), "choice confidence")
    _assert_probability(binary.get("value"), "binary probability")
    _assert_probability(binary.get("confidence"), "binary confidence")

    usage = payload.get("usage") or {}
    for key in ("prompt_tokens", "completion_tokens", "total_tokens"):
        value = usage.get(key)
        if value is not None and int(value) < 0:
            raise AssertionError(f"{key} must not be negative")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run a live end-to-end certification request against System One."
    )
    parser.add_argument(
        "--runtime-url",
        default="http://localhost:8002",
    )
    parser.add_argument(
        "--provider",
        help="Optional configured provider instance ID.",
    )
    parser.add_argument(
        "--model",
        help="Optional model override.",
    )
    args = parser.parse_args()

    payload: Dict[str, Any] = {
        "state": (
            "A production service is healthy. The request is read-only and asks "
            "for current status. No persistent state change is requested."
        ),
        "questions": {
            "choice": {
                "type": "choice",
                "instructions": "Choose the appropriate operation type.",
                "criteria": {
                    "read": "Read or inspect state without modifying it",
                    "write": "Create, update, or delete persistent state",
                },
            },
            "binary": {
                "type": "null",
                "instructions": (
                    "The request should be handled as a read-only operation."
                ),
            },
        },
    }
    if args.provider:
        payload["provider"] = args.provider
    if args.model:
        payload["model"] = args.model

    base = args.runtime_url.rstrip("/")
    with httpx.Client(timeout=120) as client:
        health = client.get(f"{base}/v1/health")
        health.raise_for_status()

        providers = client.get(f"{base}/v2/providers")
        providers.raise_for_status()

        response = client.post(f"{base}/v2/decide", json=payload)
        response.raise_for_status()
        result = response.json()

    validate_response(result)

    print(json.dumps({
        "status": "PASS",
        "health": health.json(),
        "providers": providers.json(),
        "route": result.get("route"),
        "answers": result.get("answers"),
        "usage": result.get("usage"),
        "latency_ms": result.get("latency_ms"),
    }, indent=2))


if __name__ == "__main__":
    main()
