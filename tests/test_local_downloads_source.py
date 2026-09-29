import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "demo" / "ui" / "serve_demo.py"


def _load_server_module():
    spec = importlib.util.spec_from_file_location("systemone_demo_server", SERVER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_downloads_scanner_is_read_only_and_normalizes_files(tmp_path: Path):
    module = _load_server_module()
    (tmp_path / "notes.txt").write_text(
        "hello from downloads",
        encoding="utf-8",
    )
    (tmp_path / "photo.jpg").write_bytes(
        b"not-an-image-parser-test",
    )

    before = sorted(p.name for p in tmp_path.iterdir())
    docs = module.scan_local_root(tmp_path)
    after = sorted(p.name for p in tmp_path.iterdir())

    assert before == after
    assert len(docs) == 2

    txt = next(doc for doc in docs if doc["title"] == "notes.txt")
    jpg = next(doc for doc in docs if doc["title"] == "photo.jpg")

    assert "hello from downloads" in txt["content"]
    assert txt["metadata"]["source_type"] == "local_file"
    assert txt["metadata"]["content_mode"] == "text"
    assert jpg["metadata"]["content_mode"] == "metadata"
    assert jpg["metadata"]["source_path"].endswith("photo.jpg")
