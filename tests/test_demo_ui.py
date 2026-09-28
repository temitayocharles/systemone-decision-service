from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "demo" / "ui" / "system-one-demo-ui.html").read_text()
SERVER = (ROOT / "demo" / "ui" / "serve_demo.py").read_text()


def test_ui_is_browser_first_and_uses_both_services():
    for endpoint in (
        "/rag/v1/ingest",
        "/rag/v1/retrieve",
        "/rag/v1/query",
        "/v2/decide",
        "/v2/providers",
        "/v2/metrics?limit=1000",
        "/v2/benchmarks",
    ):
        assert endpoint in HTML


def test_ui_proxy_routes_rag_and_runtime_separately():
    assert 'if self.path.startswith("/rag/")' in SERVER
    assert 'return self.rag + self.path[len("/rag"):]' in SERVER
    assert 'return self.runtime + self.path' in SERVER


def test_ui_uses_white_minimal_surface():
    assert "--surface:#fff" in HTML or "--surface:#ffffff" in HTML
    assert "--bg:#f7f8fb" in HTML or "--bg:#f6f8fb" in HTML
    assert "warm-palette" not in HTML
