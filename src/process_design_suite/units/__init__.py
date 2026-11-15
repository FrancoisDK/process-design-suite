from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

UnitCategory = Literal["pressure", "temperature", "flow", "length", "mass", "density", "viscosity", "power"]


@dataclass(frozen=True)
class UnitDefinition:
    name: str
    symbol: str
    category: UnitCategory
    canonical: bool = False


@dataclass
class UnitSystem:
    name: str = "SI"
    definitions: dict[UnitCategory, list[UnitDefinition]] = field(
        default_factory=lambda: {
            "pressure": [
                UnitDefinition("pascal", "Pa", "pressure", canonical=True),
                UnitDefinition("bar", "bar", "pressure"),
            ],
            "temperature": [
                UnitDefinition("kelvin", "K", "temperature", canonical=True),
                UnitDefinition("celsius", "°C", "temperature"),
            ],
            "flow": [
                UnitDefinition("cubic_meters_per_second", "m3/s", "flow", canonical=True),
                UnitDefinition("liters_per_minute", "L/min", "flow"),
            ],
            "length": [
                UnitDefinition("meter", "m", "length", canonical=True),
                UnitDefinition("millimeter", "mm", "length"),
            ],
            "mass": [
                UnitDefinition("kilogram", "kg", "mass", canonical=True),
                UnitDefinition("gram", "g", "mass"),
            ],
            "density": [
                UnitDefinition("kilograms_per_cubic_meter", "kg/m3", "density", canonical=True),
                UnitDefinition("grams_per_liter", "g/L", "density"),
            ],
            "viscosity": [
                UnitDefinition("pascal_second", "Pa.s", "viscosity", canonical=True),
                UnitDefinition("centipoise", "cP", "viscosity"),
            ],
            "power": [
                UnitDefinition("watt", "W", "power", canonical=True),
                UnitDefinition("kilowatt", "kW", "power"),
            ],
        }
    )

    def categories(self) -> list[str]:
        return list(self.definitions)

    def supported_units(self, category: UnitCategory) -> list[UnitDefinition]:
        return self.definitions.get(category, [])


__all__ = ["UnitCategory", "UnitDefinition", "UnitSystem"]
