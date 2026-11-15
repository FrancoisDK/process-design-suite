from __future__ import annotations

from process_design_suite.db.repository import DatabaseRepository
from process_design_suite.schemas.settings import UpdateUserPreferences, UserPreferences


class SettingsService:
    def __init__(self, database: DatabaseRepository) -> None:
        self.database = database

    def get_user_preferences(self) -> UserPreferences:
        length_unit = self.database.get_application_state("length_unit") or "mm"
        decimal_precision = self.database.get_application_state("decimal_precision") or "3"
        pressure_unit = self.database.get_application_state("pressure_unit") or "kPa"
        pressure_profile = self.database.get_application_state("pressure_profile") or "sea-level"
        atmospheric_pressure_kpa = self.database.get_application_state("atmospheric_pressure_kpa") or "101.325"

        return UserPreferences(
            length_unit=length_unit,  # validated by schema
            decimal_precision=int(decimal_precision),
            pressure_unit=pressure_unit,  # validated by schema
            pressure_profile=pressure_profile,  # validated by schema
            atmospheric_pressure_kpa=float(atmospheric_pressure_kpa),
        )

    def update_user_preferences(self, update: UpdateUserPreferences) -> UserPreferences:
        updates = update.model_dump(exclude_none=True)
        if "length_unit" in updates:
            self.database.set_application_state("length_unit", str(updates["length_unit"]))
        if "decimal_precision" in updates:
            self.database.set_application_state("decimal_precision", str(updates["decimal_precision"]))
        if "pressure_unit" in updates:
            self.database.set_application_state("pressure_unit", str(updates["pressure_unit"]))
        if "pressure_profile" in updates:
            self.database.set_application_state("pressure_profile", str(updates["pressure_profile"]))
        if "atmospheric_pressure_kpa" in updates:
            self.database.set_application_state("atmospheric_pressure_kpa", str(updates["atmospheric_pressure_kpa"]))
        return self.get_user_preferences()
