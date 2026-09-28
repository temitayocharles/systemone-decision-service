"""Legacy v1 decision-service configuration.

The v2 runtime uses provider instances from SYSTEMONE_PROVIDER_* variables.
These legacy DECIDE_* settings remain only for the preserved v1 API and have
no provider/model defaults.
"""
from __future__ import annotations

import os
from pathlib import Path


def get(name: str, default: str = "") -> str:
    value = os.getenv(name)
    if value is not None and value != "":
        return value
    return default


BASE_URL = get("DECIDE_BASE_URL", "")
API_KEY = get("DECIDE_API_KEY", "")
MODEL = get("DECIDE_MODEL", "")
REQUEST_TIMEOUT_S = float(get("DECIDE_TIMEOUT_S", "60"))
MAX_PARALLEL = int(get("DECIDE_MAX_PARALLEL", "8"))
APP_VERSION = get("APP_VERSION", "0.2.0")

DATA_DIR = Path(
    get(
        "DECIDE_DATA_DIR",
        str(Path(__file__).resolve().parent / "data"),
    )
)
TEMPERATURES_FILE = DATA_DIR / "temperatures.json"


def provider_configured() -> bool:
    # Authentication may legitimately be absent for local endpoints.
    return bool(BASE_URL and MODEL)
