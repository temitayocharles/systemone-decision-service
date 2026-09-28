from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, Mapping, Optional, Set


@dataclass(frozen=True)
class CapabilityProfile:
    provider: str
    capabilities: Set[str] = field(default_factory=set)
    attributes: Dict[str, Any] = field(default_factory=dict)

    def supports(self, required: Iterable[str], forbidden: Iterable[str] = ()) -> bool:
        required_set = set(required)
        forbidden_set = set(forbidden)
        return required_set.issubset(self.capabilities) and not (
            forbidden_set & self.capabilities
        )

    def attributes_match(
        self,
        minimum: Optional[Mapping[str, float]] = None,
        maximum: Optional[Mapping[str, float]] = None,
        equals: Optional[Mapping[str, Any]] = None,
    ) -> bool:
        for key, expected in (equals or {}).items():
            if self.attributes.get(key) != expected:
                return False
        for key, threshold in (minimum or {}).items():
            value = self.attributes.get(key)
            if not isinstance(value, (int, float)) or value < threshold:
                return False
        for key, threshold in (maximum or {}).items():
            value = self.attributes.get(key)
            if not isinstance(value, (int, float)) or value > threshold:
                return False
        return True


def parse_capabilities(value: str) -> Set[str]:
    return {item.strip() for item in value.split(",") if item.strip()}


def parse_attributes(value: str) -> Dict[str, Any]:
    if not value.strip():
        return {}
    raw = json.loads(value)
    if not isinstance(raw, dict):
        raise ValueError("provider attributes must be a JSON object")
    return raw


def derived_capabilities(driver: str) -> Set[str]:
    if driver == "openai_compatible":
        return {"chat_completions", "token_logprobs", "probabilistic_decisions"}
    if driver == "systemone_http":
        return {"native_systemone", "probabilistic_decisions"}
    if driver.startswith("python:"):
        return {"custom_driver"}
    return set()
