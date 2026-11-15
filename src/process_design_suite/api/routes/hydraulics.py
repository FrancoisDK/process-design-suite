from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from process_design_suite.schemas.hydraulics import (
    CreateHydraulicsCaseRequest,
    GasPipeHydraulicsHighDPInput,
    GasPipeHydraulicsHighDPResult,
    GasPipeHydraulicsLowDPInput,
    GasPipeHydraulicsLowDPResult,
    HydraulicsCaseDetail,
    HydraulicsCaseSummary,
    LiquidPipeHydraulicsInput,
    LiquidPipeHydraulicsResult,
    UpdateHydraulicsCaseRequest,
)
from process_design_suite.services.hydraulics_service import HydraulicsService

router = APIRouter(tags=["hydraulics"])


def get_hydraulics_service(request: Request) -> HydraulicsService:
    database = getattr(request.app.state, "database", None)
    return HydraulicsService(database=database)


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


@router.get("/hydraulics/cases", response_model=list[HydraulicsCaseSummary])
async def list_hydraulics_cases(service: HydraulicsService = Depends(get_hydraulics_service)) -> list[HydraulicsCaseSummary]:
    return service.list_cases()


@router.post("/hydraulics/cases", response_model=HydraulicsCaseDetail)
async def create_hydraulics_case(
    payload: CreateHydraulicsCaseRequest,
    service: HydraulicsService = Depends(get_hydraulics_service),
) -> HydraulicsCaseDetail:
    return service.create_case(payload)


@router.get("/hydraulics/cases/{case_id}", response_model=HydraulicsCaseDetail)
async def get_hydraulics_case(case_id: int, service: HydraulicsService = Depends(get_hydraulics_service)) -> HydraulicsCaseDetail:
    return service.get_case(case_id)


@router.delete("/hydraulics/cases/{case_id}")
async def delete_hydraulics_case(case_id: int, service: HydraulicsService = Depends(get_hydraulics_service)) -> dict[str, bool]:
    return {"deleted": service.delete_case(case_id)}


@router.patch("/hydraulics/cases/{case_id}", response_model=HydraulicsCaseDetail)
async def update_hydraulics_case(
    case_id: int,
    payload: UpdateHydraulicsCaseRequest,
    service: HydraulicsService = Depends(get_hydraulics_service),
) -> HydraulicsCaseDetail:
    return service.update_case(case_id, payload)
