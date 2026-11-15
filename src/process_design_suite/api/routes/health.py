from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from process_design_suite.schemas.health import HealthStatusResponse
from process_design_suite.services.system_service import SystemService

router = APIRouter(tags=["system"])


def get_system_service(request: Request) -> SystemService:
    settings = getattr(request.app.state, "settings", None)
    database = getattr(request.app.state, "database", None)
    return SystemService(settings=settings, database=database)


@router.get("/health", response_model=HealthStatusResponse)
async def get_health(service: SystemService = Depends(get_system_service)) -> HealthStatusResponse:
    return service.get_health()
