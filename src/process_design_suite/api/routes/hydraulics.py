from __future__ import annotations

from fastapi import APIRouter, Depends

from process_design_suite.schemas.hydraulics import (
    LiquidPipeHydraulicsInput,
    LiquidPipeHydraulicsResult,
)
from process_design_suite.services.hydraulics_service import HydraulicsService

router = APIRouter(tags=["hydraulics"])


def get_hydraulics_service() -> HydraulicsService:
    return HydraulicsService()


@router.post("/hydraulics/liquid-pipe", response_model=LiquidPipeHydraulicsResult)
async def calculate_liquid_pipe_hydraulics(
    payload: LiquidPipeHydraulicsInput,
    service: HydraulicsService = Depends(get_hydraulics_service),
) -> LiquidPipeHydraulicsResult:
    return service.calculate_liquid_pipe_hydraulics(payload)
