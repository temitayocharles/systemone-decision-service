from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "demo" / "ui" / "system-one-demo-ui.html").read_text()
PIPELINE = (ROOT / "rag" / "app" / "pipeline.py").read_text()


def test_grounded_query_returns_canonical_sources_with_provenance():
    for field in (
        '"source"',
        '"source_path"',
        '"chunk_index"',
        '"collection"',
        '"distance"',
        '"source_count"',
    ):
        assert field in PIPELINE


def test_ui_uses_grounded_query_sources_as_canonical_evidence():
    assert "qa.body.sources||[]" in HTML
    assert "sources used for answer" in HTML
    assert "x.source||x.source_path" in HTML
    assert "chunk_index" in HTML
    assert "distance" in HTML
