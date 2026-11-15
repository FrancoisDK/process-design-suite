from fastapi.testclient import TestClient

from process_design_suite.app import create_app


def test_backend_app_starts() -> None:
    app = create_app()
    client = TestClient(app)

    response = client.get("/api/v1/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["service"] == "process-design-suite"
    assert payload["database"]["type"] == "sqlite"
    assert payload["database"]["status"] == "ready"
    assert payload["readiness"] == "ready"


def test_health_response_schema_validation() -> None:
    app = create_app()
    client = TestClient(app)

    response = client.get("/api/v1/health")
    payload = response.json()

    assert "timestamp" in payload
    assert payload["version"] == "0.1.0"
    assert payload["environment"] == "development"
