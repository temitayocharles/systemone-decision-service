from __future__ import annotations

import importlib
import os
import re
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, Optional, Set

from ..capabilities import (
    CapabilityProfile,
    derived_capabilities,
    parse_attributes,
    parse_capabilities,
)
from .base import DecisionProvider
from .openai_compatible import OpenAICompatibleProvider
from .systemone_http import NativeSystemOneHTTPProvider


@dataclass(frozen=True)
class ProviderInstance:
    instance_id: str
    driver: str
    base_url: str
    model: str
    api_key: str = ""
    timeout_s: float = 60.0
    max_parallel: int = 8
    capabilities: Set[str] = field(default_factory=set)
    attributes: Dict[str, Any] = field(default_factory=dict)


def _env_prefix(instance_id: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9]+", "_", instance_id).strip("_").upper()
    if not safe:
        raise ValueError(f"invalid provider instance id: {instance_id!r}")
    return f"SYSTEMONE_PROVIDER_{safe}"


def _read_instance(instance_id: str) -> ProviderInstance:
    prefix = _env_prefix(instance_id)
    driver = os.getenv(f"{prefix}_DRIVER", "").strip()
    if not driver:
        raise ValueError(f"{prefix}_DRIVER is required")

    declared = parse_capabilities(os.getenv(f"{prefix}_CAPABILITIES", ""))
    capabilities = derived_capabilities(driver) | declared
    attributes = parse_attributes(os.getenv(f"{prefix}_ATTRIBUTES_JSON", ""))

    return ProviderInstance(
        instance_id=instance_id,
        driver=driver,
        base_url=os.getenv(f"{prefix}_BASE_URL", "").strip(),
        model=os.getenv(f"{prefix}_MODEL", "").strip(),
        api_key=os.getenv(f"{prefix}_API_KEY", ""),
        timeout_s=float(os.getenv(f"{prefix}_TIMEOUT_S", "60")),
        max_parallel=int(os.getenv(f"{prefix}_MAX_PARALLEL", "8")),
        capabilities=capabilities,
        attributes=attributes,
    )


def _load_plugin(path: str, instance: ProviderInstance) -> DecisionProvider:
    target = path.removeprefix("python:")
    if ":" in target:
        module_name, class_name = target.split(":", 1)
    else:
        module_name, class_name = target.rsplit(".", 1)
    cls = getattr(importlib.import_module(module_name), class_name)
    return cls(
        name=instance.instance_id,
        base_url=instance.base_url,
        model=instance.model,
        api_key=instance.api_key,
        timeout_s=instance.timeout_s,
        max_parallel=instance.max_parallel,
    )


def _build_provider(instance: ProviderInstance) -> DecisionProvider:
    if instance.driver == "openai_compatible":
        return OpenAICompatibleProvider(
            name=instance.instance_id,
            base_url=instance.base_url,
            model=instance.model,
            api_key=instance.api_key,
            timeout_s=instance.timeout_s,
            max_parallel=instance.max_parallel,
        )
    if instance.driver == "systemone_http":
        return NativeSystemOneHTTPProvider(
            name=instance.instance_id,
            base_url=instance.base_url,
            model=instance.model,
            api_key=instance.api_key,
            timeout_s=instance.timeout_s,
        )
    if instance.driver.startswith("python:"):
        return _load_plugin(instance.driver, instance)
    raise ValueError(
        f"unsupported driver {instance.driver!r} for provider instance {instance.instance_id!r}"
    )


class ProviderRegistry:
    def __init__(self) -> None:
        self._providers: Dict[str, DecisionProvider] = {}
        self._instances: Dict[str, ProviderInstance] = {}

        ids = [
            value.strip()
            for value in os.getenv("SYSTEMONE_PROVIDER_IDS", "").split(",")
            if value.strip()
        ]
        for instance_id in ids:
            instance = _read_instance(instance_id)
            self._instances[instance_id] = instance
            self.register(_build_provider(instance))

    def register(self, provider: DecisionProvider) -> None:
        self._providers[provider.name] = provider

    def get(self, name: str) -> DecisionProvider:
        try:
            return self._providers[name]
        except KeyError as exc:
            raise KeyError(f"unknown provider instance: {name}") from exc

    def names(self) -> Iterable[str]:
        return tuple(self._providers)

    def items(self):
        return self._providers.items()

    def first_name(self) -> Optional[str]:
        return next(iter(self._providers), None)

    def capability_profiles(self) -> Dict[str, CapabilityProfile]:
        return {
            item.instance_id: CapabilityProfile(
                provider=item.instance_id,
                capabilities=set(item.capabilities),
                attributes=dict(item.attributes),
            )
            for item in self._instances.values()
        }

    def describe(self) -> list[dict]:
        return [
            {
                "id": item.instance_id,
                "driver": item.driver,
                "base_url": item.base_url,
                "model": item.model,
                "authenticated": bool(item.api_key),
                "timeout_s": item.timeout_s,
                "max_parallel": item.max_parallel,
                "capabilities": sorted(item.capabilities),
                "attributes": item.attributes,
            }
            for item in self._instances.values()
        ]
