from pathlib import Path

from fastapi.testclient import TestClient

from process_design_suite.app import create_app
from process_design_suite.config import Settings


def _create_test_app(tmp_path: Path):
    settings = Settings(database_path=str(tmp_path / "test_settings.db"))
    return create_app(settings=settings)


def test_settings_preferences_defaults(tmp_path: Path) -> None:
    app = _create_test_app(tmp_path)
    client = TestClient(app)

    response = client.get("/api/v1/settings/preferences")

    assert response.status_code == 200
    payload = response.json()
    assert payload["length_unit"] == "mm"
    assert payload["decimal_precision"] == 3
    assert payload["pressure_unit"] == "kPa"
    assert payload["pressure_profile"] == "sea-level"
    assert payload["atmospheric_pressure_kpa"] == 101.325


def test_settings_preferences_update_persists(tmp_path: Path) -> None:
    app = _create_test_app(tmp_path)
    client = TestClient(app)

    update_payload = {
        "length_unit": "in",
        "decimal_precision": 4,
        "pressure_unit": "psia",
        "pressure_profile": "1500m",
        "atmospheric_pressure_kpa": 84.56,
    }
    update_response = client.put("/api/v1/settings/preferences", json=update_payload)

    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated["length_unit"] == "in"
    assert updated["decimal_precision"] == 4
    assert updated["pressure_unit"] == "psia"
    assert updated["pressure_profile"] == "1500m"
    assert updated["atmospheric_pressure_kpa"] == 84.56

    read_back_response = client.get("/api/v1/settings/preferences")
    assert read_back_response.status_code == 200
    read_back = read_back_response.json()
    assert read_back == updated
