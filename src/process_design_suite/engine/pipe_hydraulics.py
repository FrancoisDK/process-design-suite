from __future__ import annotations

import math
from typing import Literal

from process_design_suite.schemas.hydraulics import (
    GasPipeHydraulicsHighDPInput,
    GasPipeHydraulicsHighDPResult,
    GasPipeHydraulicsLowDPInput,
    GasPipeHydraulicsLowDPResult,
    LiquidPipeHydraulicsInput,
    LiquidPipeHydraulicsResult,
    ThreeKFittingEntry,
)

METER_TO_INCH = 39.37007874015748
R_UNIVERSAL_J_PER_KMOL_K = 8314.462618


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
        include_fittings=inputs.include_fittings,
        fittings_method=inputs.fittings_method,
        fittings_k_total=inputs.fittings_k_total,
        fittings_3k=inputs.fittings_3k,
        inside_diameter_m=inputs.inside_diameter_m,
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


def calculate_gas_pipe_hydraulics_low_dp(inputs: GasPipeHydraulicsLowDPInput) -> GasPipeHydraulicsLowDPResult:
    area_m2 = math.pi * (inputs.inside_diameter_m**2) / 4.0
    inlet_density_kg_m3 = _ideal_gas_density(
        pressure_pa=inputs.inlet_pressure_pa,
        temperature_k=inputs.gas_temperature_k,
        molecular_weight_kg_kmol=inputs.molecular_weight_kg_kmol,
        z_factor=inputs.compressibility_factor,
    )
    velocity_m_s = inputs.mass_flow_kg_s / (inlet_density_kg_m3 * area_m2)
    reynolds_number = inputs.mass_flow_kg_s * inputs.inside_diameter_m / (area_m2 * inputs.dynamic_viscosity_pa_s)
    friction_factor = _darcy_friction_factor(
        reynolds_number=reynolds_number,
        absolute_roughness_m=inputs.absolute_roughness_m,
        inside_diameter_m=inputs.inside_diameter_m,
    )
    dynamic_pressure_pa = inlet_density_kg_m3 * velocity_m_s**2 / 2.0
    straight_pipe_pressure_drop_pa = friction_factor * (inputs.pipe_length_m / inputs.inside_diameter_m) * dynamic_pressure_pa
    fittings_k_effective = _fittings_k_effective(
        include_fittings=inputs.include_fittings,
        fittings_method=inputs.fittings_method,
        fittings_k_total=inputs.fittings_k_total,
        fittings_3k=inputs.fittings_3k,
        inside_diameter_m=inputs.inside_diameter_m,
        reynolds_number=reynolds_number,
    )
    fittings_pressure_drop_pa = fittings_k_effective * dynamic_pressure_pa
    total_pressure_drop_pa = straight_pipe_pressure_drop_pa + fittings_pressure_drop_pa
    outlet_pressure_pa = max(inputs.inlet_pressure_pa - total_pressure_drop_pa, 1.0)
    mach_number = _mach_number(
        velocity_m_s=velocity_m_s,
        temperature_k=inputs.gas_temperature_k,
        molecular_weight_kg_kmol=inputs.molecular_weight_kg_kmol,
        heat_capacity_ratio=inputs.heat_capacity_ratio,
    )
    warnings: list[str] = []
    if total_pressure_drop_pa / inputs.inlet_pressure_pa > 0.1:
        warnings.append("Predicted gas pressure drop exceeds 10% of inlet pressure; use high-dP compressible model.")
    if mach_number > 0.3:
        warnings.append("Mach number exceeds 0.3; compressibility effects are significant.")
    if mach_number > 0.8:
        warnings.append("Mach number is high; evaluate choking risk with the high-dP model.")

    return GasPipeHydraulicsLowDPResult(
        inlet_density_kg_m3=inlet_density_kg_m3,
        velocity_m_s=velocity_m_s,
        reynolds_number=reynolds_number,
        mach_number=mach_number,
        friction_factor=friction_factor,
        fittings_k_effective=fittings_k_effective,
        straight_pipe_pressure_drop_pa=straight_pipe_pressure_drop_pa,
        fittings_pressure_drop_pa=fittings_pressure_drop_pa,
        total_pressure_drop_pa=total_pressure_drop_pa,
        outlet_pressure_pa=outlet_pressure_pa,
        warnings=warnings,
    )


def calculate_gas_pipe_hydraulics_high_dp(inputs: GasPipeHydraulicsHighDPInput) -> GasPipeHydraulicsHighDPResult:
    area_m2 = math.pi * (inputs.inside_diameter_m**2) / 4.0
    inlet_density_kg_m3 = _ideal_gas_density(
        pressure_pa=inputs.upstream_pressure_pa,
        temperature_k=inputs.gas_temperature_k,
        molecular_weight_kg_kmol=inputs.molecular_weight_kg_kmol,
        z_factor=inputs.compressibility_factor,
    )
    outlet_density_kg_m3 = _ideal_gas_density(
        pressure_pa=inputs.downstream_pressure_pa,
        temperature_k=inputs.gas_temperature_k,
        molecular_weight_kg_kmol=inputs.molecular_weight_kg_kmol,
        z_factor=inputs.compressibility_factor,
    )
    velocity_inlet_m_s = inputs.mass_flow_kg_s / (inlet_density_kg_m3 * area_m2)
    velocity_outlet_m_s = inputs.mass_flow_kg_s / (outlet_density_kg_m3 * area_m2)
    reynolds_number = inputs.mass_flow_kg_s * inputs.inside_diameter_m / (area_m2 * inputs.dynamic_viscosity_pa_s)
    friction_factor = _darcy_friction_factor(
        reynolds_number=reynolds_number,
        absolute_roughness_m=inputs.absolute_roughness_m,
        inside_diameter_m=inputs.inside_diameter_m,
    )
    avg_density_kg_m3 = (inlet_density_kg_m3 + outlet_density_kg_m3) / 2.0
    avg_velocity_m_s = (velocity_inlet_m_s + velocity_outlet_m_s) / 2.0
    dynamic_pressure_pa = avg_density_kg_m3 * avg_velocity_m_s**2 / 2.0
    straight_pipe_pressure_drop_pa = friction_factor * (inputs.pipe_length_m / inputs.inside_diameter_m) * dynamic_pressure_pa
    fittings_k_effective = _fittings_k_effective(
        include_fittings=inputs.include_fittings,
        fittings_method=inputs.fittings_method,
        fittings_k_total=inputs.fittings_k_total,
        fittings_3k=inputs.fittings_3k,
        inside_diameter_m=inputs.inside_diameter_m,
        reynolds_number=reynolds_number,
    )
    fittings_pressure_drop_pa = fittings_k_effective * dynamic_pressure_pa
    total_predicted_pressure_drop_pa = straight_pipe_pressure_drop_pa + fittings_pressure_drop_pa
    available_pressure_drop_pa = inputs.upstream_pressure_pa - inputs.downstream_pressure_pa
    pressure_drop_margin_pa = available_pressure_drop_pa - total_predicted_pressure_drop_pa

    pressure_ratio = inputs.downstream_pressure_pa / inputs.upstream_pressure_pa
    critical_pressure_ratio = (2.0 / (inputs.heat_capacity_ratio + 1.0)) ** (
        inputs.heat_capacity_ratio / (inputs.heat_capacity_ratio - 1.0)
    )
    choked_flow_expected = pressure_ratio <= critical_pressure_ratio
    mach_inlet = _mach_number(
        velocity_m_s=velocity_inlet_m_s,
        temperature_k=inputs.gas_temperature_k,
        molecular_weight_kg_kmol=inputs.molecular_weight_kg_kmol,
        heat_capacity_ratio=inputs.heat_capacity_ratio,
    )
    mach_outlet = _mach_number(
        velocity_m_s=velocity_outlet_m_s,
        temperature_k=inputs.gas_temperature_k,
        molecular_weight_kg_kmol=inputs.molecular_weight_kg_kmol,
        heat_capacity_ratio=inputs.heat_capacity_ratio,
    )

    warnings: list[str] = []
    if choked_flow_expected:
        warnings.append("Pressure ratio is at/below critical; choked flow is expected.")
    if mach_outlet > 0.8:
        warnings.append("Outlet Mach number is high; verify compressible-flow assumptions and line details.")
    if pressure_drop_margin_pa < 0:
        warnings.append("Predicted pressure drop exceeds available pressure drop; review line size and flow assumptions.")

    return GasPipeHydraulicsHighDPResult(
        inlet_density_kg_m3=inlet_density_kg_m3,
        outlet_density_kg_m3=outlet_density_kg_m3,
        velocity_inlet_m_s=velocity_inlet_m_s,
        velocity_outlet_m_s=velocity_outlet_m_s,
        reynolds_number=reynolds_number,
        mach_inlet=mach_inlet,
        mach_outlet=mach_outlet,
        pressure_ratio=pressure_ratio,
        critical_pressure_ratio=critical_pressure_ratio,
        choked_flow_expected=choked_flow_expected,
        friction_factor=friction_factor,
        fittings_k_effective=fittings_k_effective,
        straight_pipe_pressure_drop_pa=straight_pipe_pressure_drop_pa,
        fittings_pressure_drop_pa=fittings_pressure_drop_pa,
        total_predicted_pressure_drop_pa=total_predicted_pressure_drop_pa,
        available_pressure_drop_pa=available_pressure_drop_pa,
        pressure_drop_margin_pa=pressure_drop_margin_pa,
        warnings=warnings,
    )


def _darcy_friction_factor(reynolds_number: float, absolute_roughness_m: float, inside_diameter_m: float) -> float:
    if reynolds_number < 2300:
        return 64.0 / reynolds_number
    roughness_ratio = absolute_roughness_m / inside_diameter_m if inside_diameter_m > 0 else 0.0
    return 0.25 / (math.log10((roughness_ratio / 3.7) + (5.74 / (reynolds_number**0.9))) ** 2)


def _fittings_k_effective(
    *,
    include_fittings: bool,
    fittings_method: Literal["none", "k_total", "3k"],
    fittings_k_total: float,
    fittings_3k: list[ThreeKFittingEntry],
    inside_diameter_m: float,
    reynolds_number: float,
) -> float:
    if not include_fittings:
        return 0.0
    if fittings_method == "k_total":
        return fittings_k_total
    if fittings_method == "3k":
        return _fittings_k_3k(
            fittings_3k=fittings_3k,
            inside_diameter_m=inside_diameter_m,
            reynolds_number=reynolds_number,
        )
    return 0.0


def _fittings_k_3k(
    *,
    fittings_3k: list[ThreeKFittingEntry],
    inside_diameter_m: float,
    reynolds_number: float,
) -> float:
    diameter_in = inside_diameter_m * METER_TO_INCH
    diameter_term = diameter_in**0.3
    total_k = 0.0
    for fitting in fittings_3k:
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


def _ideal_gas_density(
    *,
    pressure_pa: float,
    temperature_k: float,
    molecular_weight_kg_kmol: float,
    z_factor: float,
) -> float:
    return pressure_pa * molecular_weight_kg_kmol / (z_factor * R_UNIVERSAL_J_PER_KMOL_K * temperature_k)


def _mach_number(
    *,
    velocity_m_s: float,
    temperature_k: float,
    molecular_weight_kg_kmol: float,
    heat_capacity_ratio: float,
) -> float:
    gas_constant_specific = R_UNIVERSAL_J_PER_KMOL_K / molecular_weight_kg_kmol
    speed_of_sound = math.sqrt(heat_capacity_ratio * gas_constant_specific * temperature_k)
    return velocity_m_s / speed_of_sound
