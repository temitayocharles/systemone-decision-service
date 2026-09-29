from pathlib import Path

from rag.app.chunker import chunk_directory_records


def test_chunk_directory_records_preserves_source_metadata(tmp_path: Path):
    source = tmp_path / "runbook.md"
    source.write_text("# Runbook\n\nCheck pod events and logs.", encoding="utf-8")

    records = chunk_directory_records(tmp_path)

    assert records
    assert records[0]["source"] == "runbook.md"
    assert records[0]["source_path"].endswith("runbook.md")
    assert records[0]["chunk_index"] == 0
    assert "Check pod events" in records[0]["text"]
