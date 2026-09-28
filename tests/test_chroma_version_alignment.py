from pathlib import Path
import re


def test_chroma_client_and_server_versions_match():
    root = Path(__file__).resolve().parents[1]
    requirements = (root / "rag" / "requirements.txt").read_text()
    compose = (root / "docker-compose.yml").read_text()

    client = re.search(r"^chromadb==([^\s]+)$", requirements, re.MULTILINE)
    server = re.search(r"image:\s*chromadb/chroma:([^\s]+)", compose)

    assert client is not None
    assert server is not None
    assert client.group(1) == server.group(1)
