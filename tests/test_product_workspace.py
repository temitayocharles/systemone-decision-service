from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "demo" / "ui" / "system-one-demo-ui.html").read_text()
VIDEO = (ROOT / "docs" / "VIDEO_RUNBOOK.md").read_text()


def test_product_ui_runs_full_connected_flow():
    for endpoint in (
        "/rag/v1/retrieve",
        "/rag/v1/query",
        "/v2/decide",
        "/v2/metrics?limit=1000",
        "/v2/benchmarks",
        "/v2/providers",
    ):
        assert endpoint in HTML


def test_product_ui_has_live_pipeline_states():
    for label in ("Retrieve", "Answer", "Decide", "Record"):
        assert label in HTML
    assert "askSystemOne()" in HTML
    assert "localStorage" in HTML


def test_viewer_runbook_explains_stack_on_camera():
    assert "High-level stack overview" in VIDEO
    for term in ("browser workspace", "RAG service", "Chroma", "Ollama", "Decision Runtime", "calibration profiles", "benchmark records", "telemetry"):
        assert term in VIDEO
