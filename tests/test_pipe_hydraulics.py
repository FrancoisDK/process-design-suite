from fastapi.testclient import TestClient

from process_design_suite.app import create_app


def test_liquid_pipe_hydraulics_returns_expected_shape() -> None:
    app = create_app()
    client = TestClient(app)

    payload = {
        "volumetric_flow_m3_s": 0.01,
        "inside_diameter_m": 0.0525,
        "pipe_length_m": 120.0,
        "fluid_density_kg_m3": 998.0,
        "dynamic_viscosity_pa_s": 0.001,
        "absolute_roughness_m": 0.000045,
        "elevation_change_m": 5.0,
        "inlet_pressure_pa": 300000.0,
        "include_fittings": True,
        "fittings_method": "k_total",
        "fittings_k_total": 12.0,
    }

    response = client.post("/api/v1/hydraulics/liquid-pipe", json=payload)

    assert response.status_code == 200
    result = response.json()
    assert result["velocity_m_s"] > 0
    assert result["reynolds_number"] > 0
    assert result["friction_factor"] > 0
    assert result["straight_pipe_pressure_drop_pa"] > 0
    assert result["fittings_k_effective"] > 0
    assert result["fittings_pressure_drop_pa"] > 0
    assert result["elevation_pressure_drop_pa"] > 0
    assert result["total_pressure_drop_pa"] > 0
    assert result["outlet_pressure_pa"] is not None
    assert isinstance(result["warnings"], list)


def test_liquid_pipe_hydraulics_3k_method_applies_fittings_losses() -> None:
    app = create_app()
    client = TestClient(app)

    payload = {
        "volumetric_flow_m3_s": 0.002,
        "inside_diameter_m": 0.02664,
        "pipe_length_m": 20.0,
        "fluid_density_kg_m3": 998.0,
        "dynamic_viscosity_pa_s": 0.0012,
        "include_fittings": True,
        "fittings_method": "3k",
        "fittings_3k": [
            {"name": "90 elbow LR", "quantity": 2, "k1": 800.0, "k_inf": 0.25, "k_d": 3.9},
            {"name": "gate valve", "quantity": 1, "k1": 300.0, "k_inf": 0.17, "k_d": 2.0},
        ],
    }

    response = client.post("/api/v1/hydraulics/liquid-pipe", json=payload)

    assert response.status_code == 200
    result = response.json()
    assert result["fittings_k_effective"] > 0
    assert result["fittings_pressure_drop_pa"] > 0
    assert all("3K fittings method is reserved" not in warning for warning in result["warnings"])


def test_liquid_pipe_hydraulics_3k_requires_entries() -> None:
    app = create_app()
    client = TestClient(app)

    payload = {
        "volumetric_flow_m3_s": 0.002,
        "inside_diameter_m": 0.02664,
        "pipe_length_m": 20.0,
        "fluid_density_kg_m3": 998.0,
        "dynamic_viscosity_pa_s": 0.0012,
        "include_fittings": True,
        "fittings_method": "3k",
    }

    response = client.post("/api/v1/hydraulics/liquid-pipe", json=payload)
    assert response.status_code == 422
