from __future__ import annotations

import sqlite3
from fractions import Fraction
from pathlib import Path

from process_design_suite.db.repository import DatabaseRepository
from process_design_suite.schemas.pipe import PipeDimension


DEFAULT_PIPE_CATALOG: list[dict[str, object]] = [
    {"nominal_size": "1/2 in", "schedule": "40", "material": "Carbon steel", "outside_diameter_in": 0.840, "wall_thickness_in": 0.109, "inside_diameter_in": 0.622, "roughness_mm": 0.045, "standard": "Nominal reference catalog"},
    {"nominal_size": "3/4 in", "schedule": "40", "material": "Carbon steel", "outside_diameter_in": 1.050, "wall_thickness_in": 0.113, "inside_diameter_in": 0.824, "roughness_mm": 0.045, "standard": "Nominal reference catalog"},
    {"nominal_size": "1 in", "schedule": "40", "material": "Carbon steel", "outside_diameter_in": 1.315, "wall_thickness_in": 0.133, "inside_diameter_in": 1.049, "roughness_mm": 0.045, "standard": "Nominal reference catalog"},
    {"nominal_size": "1.5 in", "schedule": "40", "material": "Carbon steel", "outside_diameter_in": 1.900, "wall_thickness_in": 0.145, "inside_diameter_in": 1.610, "roughness_mm": 0.045, "standard": "Nominal reference catalog"},
    {"nominal_size": "2 in", "schedule": "40", "material": "Carbon steel", "outside_diameter_in": 2.375, "wall_thickness_in": 0.154, "inside_diameter_in": 2.067, "roughness_mm": 0.045, "standard": "Nominal reference catalog"},
    {"nominal_size": "3 in", "schedule": "40", "material": "Carbon steel", "outside_diameter_in": 3.500, "wall_thickness_in": 0.216, "inside_diameter_in": 3.068, "roughness_mm": 0.045, "standard": "Nominal reference catalog"},
    {"nominal_size": "4 in", "schedule": "40", "material": "Carbon steel", "outside_diameter_in": 4.500, "wall_thickness_in": 0.237, "inside_diameter_in": 4.026, "roughness_mm": 0.045, "standard": "Nominal reference catalog"},
    {"nominal_size": "6 in", "schedule": "40", "material": "Carbon steel", "outside_diameter_in": 6.625, "wall_thickness_in": 0.280, "inside_diameter_in": 6.065, "roughness_mm": 0.045, "standard": "Nominal reference catalog"},
    {"nominal_size": "8 in", "schedule": "40", "material": "Carbon steel", "outside_diameter_in": 8.625, "wall_thickness_in": 0.322, "inside_diameter_in": 7.981, "roughness_mm": 0.045, "standard": "Nominal reference catalog"},
    {"nominal_size": "10 in", "schedule": "40", "material": "Carbon steel", "outside_diameter_in": 10.750, "wall_thickness_in": 0.365, "inside_diameter_in": 10.020, "roughness_mm": 0.045, "standard": "Nominal reference catalog"},
    {"nominal_size": "12 in", "schedule": "40", "material": "Carbon steel", "outside_diameter_in": 12.750, "wall_thickness_in": 0.406, "inside_diameter_in": 11.938, "roughness_mm": 0.045, "standard": "Nominal reference catalog"},
    {"nominal_size": "1/2 in", "schedule": "80", "material": "Carbon steel", "outside_diameter_in": 0.840, "wall_thickness_in": 0.147, "inside_diameter_in": 0.546, "roughness_mm": 0.045, "standard": "Nominal reference catalog"},
    {"nominal_size": "3/4 in", "schedule": "80", "material": "Carbon steel", "outside_diameter_in": 1.050, "wall_thickness_in": 0.154, "inside_diameter_in": 0.742, "roughness_mm": 0.045, "standard": "Nominal reference catalog"},
    {"nominal_size": "1 in", "schedule": "80", "material": "Carbon steel", "outside_diameter_in": 1.315, "wall_thickness_in": 0.179, "inside_diameter_in": 0.957, "roughness_mm": 0.045, "standard": "Nominal reference catalog"},
    {"nominal_size": "2 in", "schedule": "80", "material": "Carbon steel", "outside_diameter_in": 2.375, "wall_thickness_in": 0.218, "inside_diameter_in": 1.939, "roughness_mm": 0.045, "standard": "Nominal reference catalog"},
    {"nominal_size": "4 in", "schedule": "80", "material": "Carbon steel", "outside_diameter_in": 4.500, "wall_thickness_in": 0.337, "inside_diameter_in": 3.826, "roughness_mm": 0.045, "standard": "Nominal reference catalog"},
    {"nominal_size": "6 in", "schedule": "80", "material": "Carbon steel", "outside_diameter_in": 6.625, "wall_thickness_in": 0.432, "inside_diameter_in": 5.761, "roughness_mm": 0.045, "standard": "Nominal reference catalog"},
]


class PipeDatabaseRepository(DatabaseRepository):
    def __init__(self, database_path: str | Path | None = None) -> None:
        super().__init__(database_path)

    def initialize(self) -> None:
        super().initialize()
        with self.get_connection() as connection:
            connection.execute("DROP TABLE IF EXISTS pipe_dimensions")
            connection.execute(
                """
                CREATE TABLE pipe_dimensions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nominal_size TEXT NOT NULL,
                    schedule TEXT NOT NULL,
                    material TEXT NOT NULL,
                    outside_diameter_in REAL NOT NULL,
                    wall_thickness_in REAL NOT NULL,
                    inside_diameter_in REAL NOT NULL,
                    roughness_mm REAL,
                    standard TEXT NOT NULL
                )
                """
            )
            connection.execute(
                "CREATE UNIQUE INDEX idx_pipe_dimensions_unique ON pipe_dimensions (nominal_size, schedule, material, outside_diameter_in, wall_thickness_in, inside_diameter_in, roughness_mm, standard)"
            )
            for pipe in DEFAULT_PIPE_CATALOG:
                connection.execute(
                    """
                    INSERT OR IGNORE INTO pipe_dimensions (
                        nominal_size,
                        schedule,
                        material,
                        outside_diameter_in,
                        wall_thickness_in,
                        inside_diameter_in,
                        roughness_mm,
                        standard
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        pipe["nominal_size"],
                        pipe["schedule"],
                        pipe["material"],
                        pipe["outside_diameter_in"],
                        pipe["wall_thickness_in"],
                        pipe["inside_diameter_in"],
                        pipe["roughness_mm"],
                        pipe["standard"],
                    ),
                )

    def list_dimensions(
        self, nominal_size: str | None = None, schedule: str | None = None, material: str | None = None
    ) -> list[PipeDimension]:
        query = "SELECT * FROM pipe_dimensions WHERE 1 = 1"
        params: list[object] = []
        if nominal_size:
            query += " AND nominal_size = ?"
            params.append(nominal_size)
        if schedule:
            query += " AND schedule = ?"
            params.append(schedule)
        if material:
            query += " AND material = ?"
            params.append(material)
        query += " ORDER BY nominal_size, schedule"

        with self.get_connection() as connection:
            rows = connection.execute(query, params).fetchall()

        dimensions = [
            PipeDimension(
                id=row["id"],
                nominal_size=row["nominal_size"],
                schedule=row["schedule"],
                material=row["material"],
                outside_diameter_in=float(row["outside_diameter_in"]),
                wall_thickness_in=float(row["wall_thickness_in"]),
                inside_diameter_in=float(row["inside_diameter_in"]),
                roughness_mm=float(row["roughness_mm"]) if row["roughness_mm"] is not None else None,
                standard=row["standard"],
            )
            for row in rows
        ]
        return sorted(dimensions, key=lambda item: (self._nominal_size_key(item.nominal_size), item.schedule))

    def unique_nominal_sizes(self) -> list[str]:
        with self.get_connection() as connection:
            rows = connection.execute("SELECT DISTINCT nominal_size FROM pipe_dimensions").fetchall()
        sizes = [row[0] for row in rows]
        return sorted(sizes, key=self._nominal_size_key)

    def unique_schedules(self) -> list[str]:
        with self.get_connection() as connection:
            rows = connection.execute("SELECT DISTINCT schedule FROM pipe_dimensions ORDER BY schedule").fetchall()
        return [row[0] for row in rows]

    def unique_materials(self) -> list[str]:
        with self.get_connection() as connection:
            rows = connection.execute("SELECT DISTINCT material FROM pipe_dimensions ORDER BY material").fetchall()
        return [row[0] for row in rows]

    @staticmethod
    def _nominal_size_key(value: str) -> float:
        numeric = value.replace(" in", "").strip()
        try:
            return float(Fraction(numeric))
        except (ValueError, ZeroDivisionError):
            return float("inf")
