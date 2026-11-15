from __future__ import annotations

from process_design_suite.db.pipe_repository import PipeDatabaseRepository
from process_design_suite.schemas.pipe import PipeDimension


class PipeService:
    def __init__(self, database: PipeDatabaseRepository | None = None) -> None:
        self.database = database or PipeDatabaseRepository()

    def list_pipe_dimensions(
        self, nominal_size: str | None = None, schedule: str | None = None, material: str | None = None
    ) -> list[PipeDimension]:
        return self.database.list_dimensions(nominal_size=nominal_size, schedule=schedule, material=material)

    def nominal_sizes(self) -> list[str]:
        return self.database.unique_nominal_sizes()

    def schedules(self) -> list[str]:
        return self.database.unique_schedules()

    def materials(self) -> list[str]:
        return self.database.unique_materials()
