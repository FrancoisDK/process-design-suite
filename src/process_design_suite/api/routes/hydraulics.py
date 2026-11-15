from __future__ import annotations

from fastapi import APIRouter, Depends

from process_design_suite.schemas.hydraulics import (
    GasPipeHydraulicsHighDPInput,
    GasPipeHydraulicsHighDPResult,
    GasPipeHydraulicsLowDPInput,
    GasPipeHydraulicsLowDPResult,
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


@router.post("/hydraulics/gas-pipe/low-dp", response_model=GasPipeHydraulicsLowDPResult)
async def calculate_gas_pipe_hydraulics_low_dp(
    payload: GasPipeHydraulicsLowDPInput,
    service: HydraulicsService = Depends(get_hydraulics_service),
) -> GasPipeHydraulicsLowDPResult:
    return service.calculate_gas_pipe_hydraulics_low_dp(payload)


@router.post("/hydraulics/gas-pipe/high-dp", response_model=GasPipeHydraulicsHighDPResult)
async def calculate_gas_pipe_hydraulics_high_dp(
    payload: GasPipeHydraulicsHighDPInput,
    service: HydraulicsService = Depends(get_hydraulics_service),
) -> GasPipeHydraulicsHighDPResult:
    return service.calculate_gas_pipe_hydraulics_high_dp(payload)
