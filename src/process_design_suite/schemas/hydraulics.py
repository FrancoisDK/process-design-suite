from __future__ import annotations

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
