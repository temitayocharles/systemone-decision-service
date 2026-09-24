"""Environment-driven configuration for the decision service.

No secrets are hard-coded here. The model provider is an OpenAI-compatible
chat-completions endpoint that returns logprobs (for example, an NVIDIA
endpoint). Without DECIDE_API_KEY the service refuses to decide and answers
HTTP 502 with a clear error instead of inventing probabilities.
"""
from __future__ import annotations

import os
from pathlib import Path


def get(name: str, default: str = "") -> str:
    value = os.getenv(name)
    if value is not None and value != "":
        return value
    return default


BASE_URL = get("DECIDE_BASE_URL", "https://integrate.api.nvidia.com/v1")
API_KEY = get("DECIDE_API_KEY", "")
MODEL = get("DECIDE_MODEL", "meta/llama-3.1-70b-instruct")
REQUEST_TIMEOUT_S = float(get("DECIDE_TIMEOUT_S", "60"))
MAX_PARALLEL = int(get("DECIDE_MAX_PARALLEL", "8"))
APP_VERSION = get("APP_VERSION", "0.1.0")

# Where fitted temperatures are persisted by /v1/calibrate and read by /v1/decide.
DATA_DIR = Path(get("DECIDE_DATA_DIR", str(Path(__file__).resolve().parent / "data")))
TEMPERATURES_FILE = DATA_DIR / "temperatures.json"


def provider_configured() -> bool:
    return bool(API_KEY)
