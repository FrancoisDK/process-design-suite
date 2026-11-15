from __future__ import annotations

from fastapi import FastAPI

from process_design_suite.api.routes import health_router, pipe_router, settings_router
from process_design_suite.config import Settings, get_settings
from process_design_suite.db.pipe_repository import PipeDatabaseRepository


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved_settings = settings or get_settings()
    database = PipeDatabaseRepository(resolved_settings.database_file)
    database.initialize()

    app = FastAPI(
        title=resolved_settings.app_name,
        version=resolved_settings.app_version,
        description="Process Design Suite foundation API for engineering workflow infrastructure.",
    )
    app.state.settings = resolved_settings
    app.state.database = database
    app.include_router(health_router, prefix="/api/v1")
    app.include_router(pipe_router, prefix="/api/v1")
    app.include_router(settings_router, prefix="/api/v1")
    return app


app = create_app()
