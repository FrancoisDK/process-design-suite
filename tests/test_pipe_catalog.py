from fastapi.testclient import TestClient

from process_design_suite.app import create_app


def test_pipe_catalog_endpoint_returns_dimensions() -> None:
    app = create_app()
    client = TestClient(app)

    response = client.get("/api/v1/pipe-catalog")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) >= 10
    first = payload[0]
    assert "nominal_size" in first
    assert "dn_size" in first
    assert "schedule" in first
    assert "material" in first
    assert "inside_diameter_in" in first


def test_pipe_catalog_filters_by_nominal_dn_schedule_and_material() -> None:
    app = create_app()
    client = TestClient(app)

    response = client.get("/api/v1/pipe-catalog?nominal_size=2%20in&dn_size=DN50&schedule=40&material=Carbon%20steel")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["nominal_size"] == "2 in"
    assert payload[0]["dn_size"] == "DN50"
    assert payload[0]["schedule"] == "40"
    assert payload[0]["material"] == "Carbon steel"


def test_pipe_catalog_options_endpoint_returns_filter_values() -> None:
    app = create_app()
    client = TestClient(app)

    response = client.get("/api/v1/pipe-catalog/options")

    assert response.status_code == 200
    payload = response.json()
    assert "nominal_sizes" in payload
    assert "dn_sizes" in payload
    assert "schedules" in payload
    assert "materials" in payload
    assert "2 in" in payload["nominal_sizes"]
    assert "DN50" in payload["dn_sizes"]
    assert "40" in payload["schedules"]
    assert "Carbon steel" in payload["materials"]
    assert payload["nominal_sizes"][:3] == ["1/2 in", "3/4 in", "1 in"]
    assert payload["dn_sizes"][:3] == ["DN15", "DN20", "DN25"]
