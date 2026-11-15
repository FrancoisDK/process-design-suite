import pytest
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


def test_hydraulics_reference_case_regressions() -> None:
    app = create_app()
    client = TestClient(app)

    liquid_payload = {
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
    liquid_result = client.post("/api/v1/hydraulics/liquid-pipe", json=liquid_payload).json()
    assert liquid_result["velocity_m_s"] == pytest.approx(4.619463200853199, rel=1e-6)
    assert liquid_result["reynolds_number"] == pytest.approx(242036.77440870332, rel=1e-6)
    assert liquid_result["friction_factor"] == pytest.approx(0.02036573602489758, rel=1e-6)
    assert liquid_result["total_pressure_drop_pa"] == pytest.approx(672400.5752545076, rel=1e-6)

    gas_low_dp_payload = {
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
    gas_low_dp_result = client.post("/api/v1/hydraulics/gas-pipe/low-dp", json=gas_low_dp_payload).json()
    assert gas_low_dp_result["inlet_density_kg_m3"] == pytest.approx(3.6818067870900837, rel=1e-6)
    assert gas_low_dp_result["mach_number"] == pytest.approx(0.06444241744218883, rel=1e-6)
    assert gas_low_dp_result["friction_factor"] == pytest.approx(0.017047933277125202, rel=1e-6)
    assert gas_low_dp_result["total_pressure_drop_pa"] == pytest.approx(27542.92563923914, rel=1e-6)

    gas_high_dp_payload = {
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
    gas_high_dp_result = client.post("/api/v1/hydraulics/gas-pipe/high-dp", json=gas_high_dp_payload).json()
    assert gas_high_dp_result["pressure_ratio"] == pytest.approx(0.3888888888888889, rel=1e-6)
    assert gas_high_dp_result["critical_pressure_ratio"] == pytest.approx(0.5439270375653221, rel=1e-6)
    assert gas_high_dp_result["fittings_k_effective"] == pytest.approx(8.810937743729761, rel=1e-6)
    assert gas_high_dp_result["total_predicted_pressure_drop_pa"] == pytest.approx(358974.0185008176, rel=1e-6)


def test_hydraulics_case_crud_endpoints() -> None:
    app = create_app()
    client = TestClient(app)

    create_payload = {
        "name": "Baseline gas low-dP",
        "model": "gas-low-dp",
        "inputs": {"mass_flow_kg_s": 0.8, "inside_diameter_m": 0.1},
        "result": {"mach_number": 0.0644, "total_pressure_drop_pa": 27542.9},
        "warnings": [],
    }
    create_response = client.post("/api/v1/hydraulics/cases", json=create_payload)
    assert create_response.status_code == 200
    created = create_response.json()
    assert created["name"] == create_payload["name"]
    assert created["model"] == create_payload["model"]
    case_id = created["id"]

    list_response = client.get("/api/v1/hydraulics/cases")
    assert list_response.status_code == 200
    listed = list_response.json()
    assert any(case["id"] == case_id for case in listed)

    get_response = client.get(f"/api/v1/hydraulics/cases/{case_id}")
    assert get_response.status_code == 200
    fetched = get_response.json()
    assert fetched["inputs"]["mass_flow_kg_s"] == 0.8
    assert fetched["result"]["mach_number"] == pytest.approx(0.0644)

    delete_response = client.delete(f"/api/v1/hydraulics/cases/{case_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["deleted"] is True

    missing_delete_response = client.delete(f"/api/v1/hydraulics/cases/{case_id}")
    assert missing_delete_response.status_code == 404
