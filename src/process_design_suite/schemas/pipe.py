from __future__ import annotations

from pydantic import BaseModel, Field


class PipeDimension(BaseModel):
    id: int = Field(..., description="Internal unique record id for the pipe size entry")
    nominal_size: str = Field(..., description="Nominal pipe size using inches or DN notation")
    schedule: str = Field(..., description="Pipe schedule designation")
    material: str = Field(..., description="Material family for the nominal dimension")
    outside_diameter_in: float = Field(..., description="Outside diameter in inches")
    wall_thickness_in: float = Field(..., description="Wall thickness in inches")
    inside_diameter_in: float = Field(..., description="Inside diameter in inches")
    roughness_mm: float | None = Field(default=None, description="Representative roughness in millimeters")
    standard: str = Field(default="ASME / nominal reference", description="Reference basis for the catalog entry")


class PipeCatalogOptions(BaseModel):
    nominal_sizes: list[str] = Field(..., description="Available nominal size options from the catalog")
    schedules: list[str] = Field(..., description="Available schedule options from the catalog")
    materials: list[str] = Field(..., description="Available material options from the catalog")
