from __future__ import annotations

from typing import Any
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class ThreeKFittingEntry(BaseModel):
    name: str = Field(..., min_length=1, description="Fitting identifier for reporting")
    quantity: int = Field(default=1, ge=1, description="Number of identical fittings")
    k1: float = Field(..., ge=0, description="Laminar coefficient term K1")
    k_inf: float = Field(..., ge=0, description="Turbulent asymptotic K coefficient")
    k_d: float = Field(..., ge=0, description="Diameter correction coefficient Kd")


class LiquidPipeHydraulicsInput(BaseModel):
    volumetric_flow_m3_s: float = Field(..., gt=0, description="Volumetric liquid flow rate in m^3/s")
    inside_diameter_m: float = Field(..., gt=0, description="Pipe inside diameter in meters")
    pipe_length_m: float = Field(..., ge=0, description="Straight pipe length in meters")
    fluid_density_kg_m3: float = Field(..., gt=0, description="Liquid density in kg/m^3")
    dynamic_viscosity_pa_s: float = Field(..., gt=0, description="Dynamic viscosity in Pa·s")
    absolute_roughness_m: float = Field(default=4.5e-5, ge=0, description="Absolute roughness in meters")
    elevation_change_m: float = Field(default=0.0, description="Elevation increase from inlet to outlet in meters")
    gravity_m_s2: float = Field(default=9.80665, gt=0, description="Gravitational acceleration in m/s^2")
    inlet_pressure_pa: float | None = Field(default=None, gt=0, description="Optional inlet pressure in Pa (absolute)")
    include_fittings: bool = Field(default=False, description="Include fittings pressure loss term")
    fittings_method: Literal["none", "k_total", "3k"] = Field(
        default="none",
        description="Fittings loss method. 3k uses Darby 3K coefficients.",
    )
    fittings_k_total: float = Field(default=0.0, ge=0, description="Total dimensionless K value for fittings")
    fittings_3k: list[ThreeKFittingEntry] = Field(
        default_factory=list,
        description="Optional Darby 3K fitting entries used when fittings_method is '3k'",
    )

    @model_validator(mode="after")
    def validate_fittings_configuration(self) -> "LiquidPipeHydraulicsInput":
        if self.fittings_method == "k_total" and not self.include_fittings:
            raise ValueError("include_fittings must be true when fittings_method is 'k_total'")
        if self.fittings_method == "none" and self.fittings_k_total > 0:
            raise ValueError("fittings_k_total must be 0 when fittings_method is 'none'")
        if self.fittings_method == "3k" and not self.include_fittings:
            raise ValueError("include_fittings must be true when fittings_method is '3k'")
        if self.fittings_method == "3k" and len(self.fittings_3k) == 0:
            raise ValueError("fittings_3k entries are required when fittings_method is '3k'")
        if self.fittings_method != "3k" and len(self.fittings_3k) > 0:
            raise ValueError("fittings_3k entries are only allowed when fittings_method is '3k'")
        return self


class LiquidPipeHydraulicsResult(BaseModel):
    velocity_m_s: float = Field(..., description="Bulk velocity in m/s")
    reynolds_number: float = Field(..., description="Reynolds number")
    friction_factor: float = Field(..., description="Darcy friction factor")
    straight_pipe_pressure_drop_pa: float = Field(..., description="Pressure drop due to straight-pipe friction in Pa")
    fittings_k_effective: float = Field(..., description="Effective aggregate fittings K value used in the run")
    fittings_pressure_drop_pa: float = Field(..., description="Pressure drop due to fittings in Pa")
    elevation_pressure_drop_pa: float = Field(..., description="Pressure drop due to elevation gain in Pa")
    total_pressure_drop_pa: float = Field(..., description="Total pressure drop in Pa")
    outlet_pressure_pa: float | None = Field(default=None, description="Outlet pressure in Pa when inlet pressure is provided")
    warnings: list[str] = Field(default_factory=list, description="Engineering warnings")


class GasPipeHydraulicsLowDPInput(BaseModel):
    mass_flow_kg_s: float = Field(..., gt=0, description="Gas mass flow in kg/s")
    inside_diameter_m: float = Field(..., gt=0, description="Pipe inside diameter in meters")
    pipe_length_m: float = Field(..., ge=0, description="Straight pipe length in meters")
    inlet_pressure_pa: float = Field(..., gt=0, description="Inlet pressure in Pa (absolute)")
    gas_temperature_k: float = Field(..., gt=0, description="Gas temperature in Kelvin")
    molecular_weight_kg_kmol: float = Field(..., gt=0, description="Gas molecular weight in kg/kmol")
    compressibility_factor: float = Field(default=1.0, gt=0, description="Compressibility factor Z")
    heat_capacity_ratio: float = Field(default=1.4, gt=1.0, description="Heat capacity ratio gamma")
    dynamic_viscosity_pa_s: float = Field(..., gt=0, description="Gas dynamic viscosity in Pa·s")
    absolute_roughness_m: float = Field(default=4.5e-5, ge=0, description="Absolute roughness in meters")
    include_fittings: bool = Field(default=False, description="Include fittings pressure loss term")
    fittings_method: Literal["none", "k_total", "3k"] = Field(default="none", description="Fittings loss method")
    fittings_k_total: float = Field(default=0.0, ge=0, description="Total dimensionless K value for fittings")
    fittings_3k: list[ThreeKFittingEntry] = Field(default_factory=list, description="Darby 3K fitting entries")

    @model_validator(mode="after")
    def validate_fittings_configuration(self) -> "GasPipeHydraulicsLowDPInput":
        if self.fittings_method == "k_total" and not self.include_fittings:
            raise ValueError("include_fittings must be true when fittings_method is 'k_total'")
        if self.fittings_method == "none" and self.fittings_k_total > 0:
            raise ValueError("fittings_k_total must be 0 when fittings_method is 'none'")
        if self.fittings_method == "3k" and not self.include_fittings:
            raise ValueError("include_fittings must be true when fittings_method is '3k'")
        if self.fittings_method == "3k" and len(self.fittings_3k) == 0:
            raise ValueError("fittings_3k entries are required when fittings_method is '3k'")
        if self.fittings_method != "3k" and len(self.fittings_3k) > 0:
            raise ValueError("fittings_3k entries are only allowed when fittings_method is '3k'")
        return self


class GasPipeHydraulicsLowDPResult(BaseModel):
    inlet_density_kg_m3: float = Field(..., description="Gas density at inlet in kg/m^3")
    velocity_m_s: float = Field(..., description="Gas velocity in m/s")
    reynolds_number: float = Field(..., description="Reynolds number")
    mach_number: float = Field(..., description="Mach number at inlet conditions")
    friction_factor: float = Field(..., description="Darcy friction factor")
    fittings_k_effective: float = Field(..., description="Effective aggregate fittings K value used in the run")
    straight_pipe_pressure_drop_pa: float = Field(..., description="Pressure drop due to straight-pipe friction in Pa")
    fittings_pressure_drop_pa: float = Field(..., description="Pressure drop due to fittings in Pa")
    total_pressure_drop_pa: float = Field(..., description="Total pressure drop in Pa")
    outlet_pressure_pa: float = Field(..., description="Predicted outlet pressure in Pa (absolute)")
    warnings: list[str] = Field(default_factory=list, description="Engineering warnings")


class GasPipeHydraulicsHighDPInput(BaseModel):
    mass_flow_kg_s: float = Field(..., gt=0, description="Gas mass flow in kg/s")
    inside_diameter_m: float = Field(..., gt=0, description="Pipe inside diameter in meters")
    pipe_length_m: float = Field(..., ge=0, description="Straight pipe length in meters")
    upstream_pressure_pa: float = Field(..., gt=0, description="Upstream pressure in Pa (absolute)")
    downstream_pressure_pa: float = Field(..., gt=0, description="Downstream pressure in Pa (absolute)")
    gas_temperature_k: float = Field(..., gt=0, description="Gas temperature in Kelvin")
    molecular_weight_kg_kmol: float = Field(..., gt=0, description="Gas molecular weight in kg/kmol")
    compressibility_factor: float = Field(default=1.0, gt=0, description="Compressibility factor Z")
    heat_capacity_ratio: float = Field(default=1.4, gt=1.0, description="Heat capacity ratio gamma")
    dynamic_viscosity_pa_s: float = Field(..., gt=0, description="Gas dynamic viscosity in Pa·s")
    absolute_roughness_m: float = Field(default=4.5e-5, ge=0, description="Absolute roughness in meters")
    include_fittings: bool = Field(default=False, description="Include fittings pressure loss term")
    fittings_method: Literal["none", "k_total", "3k"] = Field(default="none", description="Fittings loss method")
    fittings_k_total: float = Field(default=0.0, ge=0, description="Total dimensionless K value for fittings")
    fittings_3k: list[ThreeKFittingEntry] = Field(default_factory=list, description="Darby 3K fitting entries")

    @model_validator(mode="after")
    def validate_configuration(self) -> "GasPipeHydraulicsHighDPInput":
        if self.downstream_pressure_pa >= self.upstream_pressure_pa:
            raise ValueError("downstream_pressure_pa must be less than upstream_pressure_pa")
        if self.fittings_method == "k_total" and not self.include_fittings:
            raise ValueError("include_fittings must be true when fittings_method is 'k_total'")
        if self.fittings_method == "none" and self.fittings_k_total > 0:
            raise ValueError("fittings_k_total must be 0 when fittings_method is 'none'")
        if self.fittings_method == "3k" and not self.include_fittings:
            raise ValueError("include_fittings must be true when fittings_method is '3k'")
        if self.fittings_method == "3k" and len(self.fittings_3k) == 0:
            raise ValueError("fittings_3k entries are required when fittings_method is '3k'")
        if self.fittings_method != "3k" and len(self.fittings_3k) > 0:
            raise ValueError("fittings_3k entries are only allowed when fittings_method is '3k'")
        return self


class GasPipeHydraulicsHighDPResult(BaseModel):
    inlet_density_kg_m3: float = Field(..., description="Gas density at upstream conditions in kg/m^3")
    outlet_density_kg_m3: float = Field(..., description="Gas density at downstream conditions in kg/m^3")
    velocity_inlet_m_s: float = Field(..., description="Gas velocity at upstream conditions in m/s")
    velocity_outlet_m_s: float = Field(..., description="Gas velocity at downstream conditions in m/s")
    reynolds_number: float = Field(..., description="Reynolds number based on inlet conditions")
    mach_inlet: float = Field(..., description="Inlet Mach number")
    mach_outlet: float = Field(..., description="Outlet Mach number")
    pressure_ratio: float = Field(..., description="Downstream to upstream pressure ratio P2/P1")
    critical_pressure_ratio: float = Field(..., description="Critical pressure ratio for choking")
    choked_flow_expected: bool = Field(..., description="True when pressure ratio is at or below critical ratio")
    friction_factor: float = Field(..., description="Darcy friction factor")
    fittings_k_effective: float = Field(..., description="Effective aggregate fittings K value used in the run")
    straight_pipe_pressure_drop_pa: float = Field(..., description="Predicted straight-pipe pressure drop in Pa")
    fittings_pressure_drop_pa: float = Field(..., description="Predicted fittings pressure drop in Pa")
    total_predicted_pressure_drop_pa: float = Field(..., description="Predicted total pressure drop in Pa")
    available_pressure_drop_pa: float = Field(..., description="Available pressure drop P1-P2 in Pa")
    pressure_drop_margin_pa: float = Field(..., description="Available minus predicted pressure drop in Pa")
    warnings: list[str] = Field(default_factory=list, description="Engineering warnings")


class CreateHydraulicsCaseRequest(BaseModel):
    name: str = Field(..., min_length=1, description="Display name for the saved hydraulics case")
    model: Literal["liquid", "gas-low-dp", "gas-high-dp"] = Field(..., description="Hydraulics model identifier")
    inputs: dict[str, Any] = Field(..., description="Input payload used for the calculation")
    result: dict[str, Any] = Field(..., description="Calculation result payload")
    warnings: list[str] = Field(default_factory=list, description="Warning list from the run")


class HydraulicsCaseSummary(BaseModel):
    id: int = Field(..., description="Saved hydraulics case identifier")
    name: str = Field(..., description="Display name for the case")
    model: Literal["liquid", "gas-low-dp", "gas-high-dp"] = Field(..., description="Hydraulics model identifier")
    created_at: str = Field(..., description="UTC timestamp when case was saved")


class HydraulicsCaseDetail(HydraulicsCaseSummary):
    inputs: dict[str, Any] = Field(..., description="Input payload used for the calculation")
    result: dict[str, Any] = Field(..., description="Calculation result payload")
    warnings: list[str] = Field(default_factory=list, description="Warning list from the run")
