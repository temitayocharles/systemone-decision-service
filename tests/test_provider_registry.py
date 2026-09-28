from decide.providers.registry import ProviderRegistry


def test_registry_uses_arbitrary_environment_instances(monkeypatch):
    monkeypatch.setenv("SYSTEMONE_PROVIDER_IDS", "alpha,local-box")
    monkeypatch.setenv("SYSTEMONE_PROVIDER_ALPHA_DRIVER", "openai_compatible")
    monkeypatch.setenv("SYSTEMONE_PROVIDER_ALPHA_BASE_URL", "https://example.invalid/v1")
    monkeypatch.setenv("SYSTEMONE_PROVIDER_ALPHA_MODEL", "model-x")
    monkeypatch.setenv("SYSTEMONE_PROVIDER_ALPHA_API_KEY", "secret")
    monkeypatch.setenv(
        "SYSTEMONE_PROVIDER_ALPHA_CAPABILITIES",
        "multimodal,structured_output",
    )
    monkeypatch.setenv(
        "SYSTEMONE_PROVIDER_ALPHA_ATTRIBUTES_JSON",
        '{"max_context":128000,"local":false}',
    )

    monkeypatch.setenv("SYSTEMONE_PROVIDER_LOCAL_BOX_DRIVER", "openai_compatible")
    monkeypatch.setenv("SYSTEMONE_PROVIDER_LOCAL_BOX_BASE_URL", "http://127.0.0.1:9999/v1")
    monkeypatch.setenv("SYSTEMONE_PROVIDER_LOCAL_BOX_MODEL", "model-y")
    monkeypatch.setenv("SYSTEMONE_PROVIDER_LOCAL_BOX_CAPABILITIES", "private_runtime")
    monkeypatch.setenv(
        "SYSTEMONE_PROVIDER_LOCAL_BOX_ATTRIBUTES_JSON",
        '{"max_context":32768,"local":true}',
    )
    monkeypatch.delenv("SYSTEMONE_PROVIDER_LOCAL_BOX_API_KEY", raising=False)

    registry = ProviderRegistry()

    assert tuple(registry.names()) == ("alpha", "local-box")
    descriptions = {item["id"]: item for item in registry.describe()}
    assert descriptions["alpha"]["model"] == "model-x"
    assert descriptions["alpha"]["authenticated"] is True
    assert "token_logprobs" in descriptions["alpha"]["capabilities"]
    assert "multimodal" in descriptions["alpha"]["capabilities"]
    assert descriptions["alpha"]["attributes"]["max_context"] == 128000
    assert descriptions["local-box"]["authenticated"] is False
    assert descriptions["local-box"]["attributes"]["local"] is True
