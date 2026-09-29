from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "demo" / "ui" / "system-one-demo-ui.html").read_text()
RUNBOOK = (ROOT / "docs" / "RUNBOOK.md").read_text()
API = (ROOT / "decide" / "runtime_api.py").read_text()


def test_provider_routing_controls_use_live_runtime_contract():
    for value in (
        'value="default"',
        'value="empirical"',
        'value="ensemble"',
        'provider:',
    ):
        assert value in HTML
    assert "/v2/providers" in HTML
    assert "/v2/benchmarks" in HTML
    assert "/v2/calibration/profiles" in HTML
    assert "Compare providers" in HTML


def test_decision_payload_keeps_routing_modes_mutually_exclusive():
    assert 'payload.policy={task_type:"generic",require_healthy:true}' in HTML
    assert 'payload.ensemble=configuredProviders.map(x=>x.id)' in HTML
    assert 'payload.provider=mode.slice(9)' in HTML


def test_runtime_exposes_read_only_calibration_profiles():
    assert '@app.get("/v2/calibration/profiles")' in API


def test_runbook_teaches_architecture_before_ui_and_provider_modes():
    lower = RUNBOOK.lower()
    for phrase in (
        "walk through the repository architecture first",
        "rag/ — the evidence service",
        "eval/ — measured evidence about providers",
        "decide/ — system one itself",
        "tests/ — proving contracts before the demo",
        "default provider",
        "explicit local provider",
        "explicit cloud provider",
        "empirical selection",
        "ensemble",
        "compare configured providers side by side",
        "calibration",
        "telemetry",
    ):
        assert phrase in lower
