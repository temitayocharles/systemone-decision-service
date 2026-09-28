from __future__ import annotations

from typing import Any, Dict, Iterable


def latest_health(events: Iterable[Dict[str, Any]]) -> Dict[str, bool]:
    """Derive current observed health from the latest runtime event per instance.

    No observation means unknown, not unhealthy. Only an observed latest error
    excludes an instance when policy requires health.
    """
    latest: Dict[str, Dict[str, Any]] = {}
    for event in events:
        provider = event.get("provider")
        if not provider:
            continue
        previous = latest.get(provider)
        if previous is None or float(event.get("ts", 0)) >= float(previous.get("ts", 0)):
            latest[provider] = event
    return {
        provider: event.get("status") == "ok"
        for provider, event in latest.items()
    }
