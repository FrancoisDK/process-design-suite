from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


LengthUnit = Literal["mm", "in"]
PressureUnit = Literal["kPa", "bar", "psia"]
PressureProfile = Literal["sea-level", "500m", "1000m", "1500m", "2000m", "custom"]


class UserPreferences(BaseModel):
    length_unit: LengthUnit = "mm"
    decimal_precision: int = Field(default=3, ge=2, le=4)
    pressure_unit: PressureUnit = "kPa"
    pressure_profile: PressureProfile = "sea-level"
    atmospheric_pressure_kpa: float = Field(default=101.325, gt=0)


class UpdateUserPreferences(BaseModel):
    length_unit: LengthUnit | None = None
    decimal_precision: int | None = Field(default=None, ge=2, le=4)
    pressure_unit: PressureUnit | None = None
    pressure_profile: PressureProfile | None = None
    atmospheric_pressure_kpa: float | None = Field(default=None, gt=0)
