from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Request

from process_design_suite.schemas.pipe import PipeCatalogOptions, PipeDimension
from process_design_suite.services.pipe_service import PipeService

router = APIRouter(tags=["pipe catalog"])


def get_pipe_service(request: Request) -> PipeService:
    database = getattr(request.app.state, "database", None)
    return PipeService(database=database)


@router.get("/pipe-catalog", response_model=list[PipeDimension])
async def get_pipe_catalog(
    nominal_size: str | None = Query(default=None, description="Optional nominal pipe size filter"),
    schedule: str | None = Query(default=None, description="Optional schedule filter"),
    material: str | None = Query(default=None, description="Optional material filter"),
    service: PipeService = Depends(get_pipe_service),
) -> list[PipeDimension]:
    return service.list_pipe_dimensions(nominal_size=nominal_size, schedule=schedule, material=material)


@router.get("/pipe-catalog/options", response_model=PipeCatalogOptions)
async def get_pipe_catalog_options(service: PipeService = Depends(get_pipe_service)) -> PipeCatalogOptions:
    return PipeCatalogOptions(
        nominal_sizes=service.nominal_sizes(),
        schedules=service.schedules(),
        materials=service.materials(),
    )
