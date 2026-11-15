from __future__ import annotations

from datetime import datetime, timezone

from process_design_suite.config import Settings
from process_design_suite.db.repository import DatabaseRepository
from process_design_suite.schemas.health import DatabaseHealth, HealthStatusResponse


class SystemService:
    def __init__(self, settings: Settings | None = None, database: DatabaseRepository | None = None) -> None:
        self.settings = settings or Settings()
        self.database = database or DatabaseRepository(self.settings.database_file)

    def get_health(self) -> HealthStatusResponse:
        database_status = self.database.health_check()
        is_ready = database_status.get("status") == "ready"

        return HealthStatusResponse(
            status="ok" if is_ready else "degraded",
            service=self.settings.app_name,
            version=self.settings.app_version,
            environment=self.settings.environment,
            timestamp=datetime.now(timezone.utc),
            database=DatabaseHealth(**database_status),
            readiness="ready" if is_ready else "not_ready",
        )
