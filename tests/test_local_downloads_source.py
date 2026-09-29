from pathlib import Path

from demo.ui.serve_demo import scan_local_root


def test_downloads_scanner_is_read_only_and_normalizes_files(tmp_path: Path):
    (tmp_path / "notes.txt").write_text("hello from downloads", encoding="utf-8")
    (tmp_path / "photo.jpg").write_bytes(b"not-an-image-parser-test")

    docs = scan_local_root(tmp_path)

    assert len(docs) == 2
    txt = next(doc for doc in docs if doc["title"] == "notes.txt")
    jpg = next(doc for doc in docs if doc["title"] == "photo.jpg")

    assert "hello from downloads" in txt["content"]
    assert txt["metadata"]["source_type"] == "local_file"
    assert txt["metadata"]["content_mode"] == "text"
    assert jpg["metadata"]["content_mode"] == "metadata"
    assert jpg["metadata"]["source_path"].endswith("photo.jpg")
