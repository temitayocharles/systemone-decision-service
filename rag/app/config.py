import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
CORPORA_DIR = BASE_DIR / "corpora"

DEFAULTS = {
    "LLM_PROVIDER": "ollama",
    "LLM_MODEL": "qwen2.5:3b",
    "EMBED_MODEL": "nomic-embed-text",
    "OLLAMA_HOST": "http://localhost:11434",
    "CHROMA_HOST": "localhost",
    "CHROMA_PORT": "8000",
    "RAG_PORT": "8001",
}


def get_setting(name: str, default: str | None = None) -> str:
    value = os.getenv(name)
    if value is not None and value != "":
        return value
    if default is not None:
        return default
    return DEFAULTS.get(name, "")


def get_collection_dir(name: str) -> Path:
    return CORPORA_DIR / name
