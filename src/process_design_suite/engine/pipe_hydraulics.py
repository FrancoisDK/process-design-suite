from __future__ import annotations

import math

from process_design_suite.schemas.hydraulics import LiquidPipeHydraulicsInput, LiquidPipeHydraulicsResult

METER_TO_INCH = 39.37007874015748


def calculate_liquid_pipe_hydraulics(inputs: LiquidPipeHydraulicsInput) -> LiquidPipeHydraulicsResult:
    area_m2 = math.pi * (inputs.inside_diameter_m**2) / 4.0
    velocity_m_s = inputs.volumetric_flow_m3_s / area_m2
    reynolds_number = (
        inputs.fluid_density_kg_m3 * velocity_m_s * inputs.inside_diameter_m / inputs.dynamic_viscosity_pa_s
    )
    friction_factor = _darcy_friction_factor(
        reynolds_number=reynolds_number,
        absolute_roughness_m=inputs.absolute_roughness_m,
        inside_diameter_m=inputs.inside_diameter_m,
    )

    dynamic_pressure_pa = inputs.fluid_density_kg_m3 * velocity_m_s**2 / 2.0
    straight_pipe_pressure_drop_pa = friction_factor * (inputs.pipe_length_m / inputs.inside_diameter_m) * dynamic_pressure_pa
    elevation_pressure_drop_pa = inputs.fluid_density_kg_m3 * inputs.gravity_m_s2 * inputs.elevation_change_m
    fittings_k_effective = _fittings_k_effective(
        inputs=inputs,
        reynolds_number=reynolds_number,
    )
    fittings_pressure_drop_pa = fittings_k_effective * dynamic_pressure_pa
    total_pressure_drop_pa = straight_pipe_pressure_drop_pa + fittings_pressure_drop_pa + elevation_pressure_drop_pa
    outlet_pressure_pa = (
        max(inputs.inlet_pressure_pa - total_pressure_drop_pa, 0.0)
        if inputs.inlet_pressure_pa is not None
        else None
    )

    warnings = _warning_messages(inputs=inputs, reynolds_number=reynolds_number, velocity_m_s=velocity_m_s)
    return LiquidPipeHydraulicsResult(
        velocity_m_s=velocity_m_s,
        reynolds_number=reynolds_number,
        friction_factor=friction_factor,
        straight_pipe_pressure_drop_pa=straight_pipe_pressure_drop_pa,
        fittings_k_effective=fittings_k_effective,
        fittings_pressure_drop_pa=fittings_pressure_drop_pa,
        elevation_pressure_drop_pa=elevation_pressure_drop_pa,
        total_pressure_drop_pa=total_pressure_drop_pa,
        outlet_pressure_pa=outlet_pressure_pa,
        warnings=warnings,
    )


def _darcy_friction_factor(reynolds_number: float, absolute_roughness_m: float, inside_diameter_m: float) -> float:
    if reynolds_number < 2300:
        return 64.0 / reynolds_number
    roughness_ratio = absolute_roughness_m / inside_diameter_m if inside_diameter_m > 0 else 0.0
    return 0.25 / (math.log10((roughness_ratio / 3.7) + (5.74 / (reynolds_number**0.9))) ** 2)


def _fittings_k_effective(inputs: LiquidPipeHydraulicsInput, reynolds_number: float) -> float:
    if not inputs.include_fittings:
        return 0.0
    if inputs.fittings_method == "k_total":
        return inputs.fittings_k_total
    if inputs.fittings_method == "3k":
        return _fittings_k_3k(inputs=inputs, reynolds_number=reynolds_number)
    return 0.0


def _fittings_k_3k(inputs: LiquidPipeHydraulicsInput, reynolds_number: float) -> float:
    diameter_in = inputs.inside_diameter_m * METER_TO_INCH
    diameter_term = diameter_in**0.3
    total_k = 0.0
    for fitting in inputs.fittings_3k:
        fitting_k = (fitting.k1 / reynolds_number) + (fitting.k_inf * (1.0 + (fitting.k_d / diameter_term)))
        total_k += fitting.quantity * fitting_k
    return total_k


def _warning_messages(inputs: LiquidPipeHydraulicsInput, reynolds_number: float, velocity_m_s: float) -> list[str]:
    warnings: list[str] = []
    if reynolds_number < 4000:
        warnings.append("Flow is in the laminar/transitional region; validate friction-factor assumptions.")
    if velocity_m_s > 5.0:
        warnings.append("Velocity exceeds 5 m/s; review erosional velocity and noise criteria.")
    if inputs.include_fittings and inputs.fittings_method == "none":
        warnings.append("Fittings are enabled but fittings_method is 'none'; fittings losses are excluded.")
    return warnings
