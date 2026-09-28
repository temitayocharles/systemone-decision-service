from fastapi.testclient import TestClient

from decide.runtime_api import app


def test_health_is_unversioned():
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_legacy_v1_runtime_routes_do_not_exist():
    with TestClient(app) as client:
        assert client.get("/v1/health").status_code == 404
        assert client.post("/v1/decide", json={}).status_code == 404
        assert client.post("/v1/calibrate", json={}).status_code == 404
