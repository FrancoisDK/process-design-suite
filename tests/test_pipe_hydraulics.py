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


def test_gas_pipe_hydraulics_low_dp_endpoint() -> None:
    app = create_app()
    client = TestClient(app)

    payload = {
        "mass_flow_kg_s": 0.8,
        "inside_diameter_m": 0.1,
        "pipe_length_m": 100.0,
        "inlet_pressure_pa": 500000.0,
        "gas_temperature_k": 300.0,
        "molecular_weight_kg_kmol": 18.0,
        "compressibility_factor": 0.98,
        "heat_capacity_ratio": 1.33,
        "dynamic_viscosity_pa_s": 1.2e-5,
        "include_fittings": True,
        "fittings_method": "k_total",
        "fittings_k_total": 2.5,
    }

    response = client.post("/api/v1/hydraulics/gas-pipe/low-dp", json=payload)

    assert response.status_code == 200
    result = response.json()
    assert result["inlet_density_kg_m3"] > 0
    assert result["velocity_m_s"] > 0
    assert result["reynolds_number"] > 0
    assert result["mach_number"] > 0
    assert result["total_pressure_drop_pa"] > 0
    assert result["outlet_pressure_pa"] > 0


def test_gas_pipe_hydraulics_high_dp_endpoint_flags_choked_condition() -> None:
    app = create_app()
    client = TestClient(app)

    payload = {
        "mass_flow_kg_s": 1.2,
        "inside_diameter_m": 0.08,
        "pipe_length_m": 150.0,
        "upstream_pressure_pa": 900000.0,
        "downstream_pressure_pa": 350000.0,
        "gas_temperature_k": 310.0,
        "molecular_weight_kg_kmol": 20.0,
        "compressibility_factor": 0.95,
        "heat_capacity_ratio": 1.31,
        "dynamic_viscosity_pa_s": 1.5e-5,
        "include_fittings": True,
        "fittings_method": "3k",
        "fittings_3k": [
            {"name": "tee through-run", "quantity": 2, "k1": 150.0, "k_inf": 0.2, "k_d": 1.0},
            {"name": "globe valve", "quantity": 1, "k1": 1000.0, "k_inf": 6.0, "k_d": 0.5},
        ],
    }

    response = client.post("/api/v1/hydraulics/gas-pipe/high-dp", json=payload)

    assert response.status_code == 200
    result = response.json()
    assert result["pressure_ratio"] < 1.0
    assert result["critical_pressure_ratio"] < 1.0
    assert result["choked_flow_expected"] is True
    assert result["fittings_k_effective"] > 0
    assert result["mach_outlet"] > 0
