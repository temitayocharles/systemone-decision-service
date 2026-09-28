from decide.providers.registry import ProviderRegistry


def test_registry_uses_arbitrary_environment_instances(monkeypatch):
    monkeypatch.setenv("SYSTEMONE_PROVIDER_IDS", "alpha,local-box")
    monkeypatch.setenv("SYSTEMONE_PROVIDER_ALPHA_DRIVER", "openai_compatible")
    monkeypatch.setenv("SYSTEMONE_PROVIDER_ALPHA_BASE_URL", "https://example.invalid/v1")
    monkeypatch.setenv("SYSTEMONE_PROVIDER_ALPHA_MODEL", "model-x")
    monkeypatch.setenv("SYSTEMONE_PROVIDER_ALPHA_API_KEY", "secret")

    monkeypatch.setenv("SYSTEMONE_PROVIDER_LOCAL_BOX_DRIVER", "openai_compatible")
    monkeypatch.setenv("SYSTEMONE_PROVIDER_LOCAL_BOX_BASE_URL", "http://127.0.0.1:9999/v1")
    monkeypatch.setenv("SYSTEMONE_PROVIDER_LOCAL_BOX_MODEL", "model-y")
    monkeypatch.delenv("SYSTEMONE_PROVIDER_LOCAL_BOX_API_KEY", raising=False)

    registry = ProviderRegistry()

    assert tuple(registry.names()) == ("alpha", "local-box")
    descriptions = {item["id"]: item for item in registry.describe()}
    assert descriptions["alpha"]["model"] == "model-x"
    assert descriptions["alpha"]["authenticated"] is True
    assert descriptions["local-box"]["model"] == "model-y"
    assert descriptions["local-box"]["authenticated"] is False
