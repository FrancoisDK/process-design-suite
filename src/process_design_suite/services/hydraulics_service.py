from __future__ import annotations

from fastapi import HTTPException

from process_design_suite.db.repository import DatabaseRepository
from process_design_suite.engine.pipe_hydraulics import (
    calculate_gas_pipe_hydraulics_high_dp,
    calculate_gas_pipe_hydraulics_low_dp,
    calculate_liquid_pipe_hydraulics,
)
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
)


class HydraulicsService:
    def __init__(self, database: DatabaseRepository | None = None) -> None:
        self.database = database

    def calculate_liquid_pipe_hydraulics(
        self, inputs: LiquidPipeHydraulicsInput
    ) -> LiquidPipeHydraulicsResult:
        return calculate_liquid_pipe_hydraulics(inputs)

    def calculate_gas_pipe_hydraulics_low_dp(
        self, inputs: GasPipeHydraulicsLowDPInput
    ) -> GasPipeHydraulicsLowDPResult:
        return calculate_gas_pipe_hydraulics_low_dp(inputs)

    def calculate_gas_pipe_hydraulics_high_dp(
        self, inputs: GasPipeHydraulicsHighDPInput
    ) -> GasPipeHydraulicsHighDPResult:
        return calculate_gas_pipe_hydraulics_high_dp(inputs)

    def list_cases(self) -> list[HydraulicsCaseSummary]:
        database = self._require_database()
        rows = database.list_hydraulics_cases()
        return [HydraulicsCaseSummary(**row) for row in rows]

    def create_case(self, payload: CreateHydraulicsCaseRequest) -> HydraulicsCaseDetail:
        database = self._require_database()
        case_id = database.create_hydraulics_case(
            name=payload.name,
            model=payload.model,
            inputs=payload.inputs,
            result=payload.result,
            warnings=payload.warnings,
        )
        case = database.get_hydraulics_case(case_id)
        if case is None:
            raise HTTPException(status_code=500, detail="Failed to read saved hydraulics case")
        return HydraulicsCaseDetail(**case)

    def get_case(self, case_id: int) -> HydraulicsCaseDetail:
        database = self._require_database()
        case = database.get_hydraulics_case(case_id)
        if case is None:
            raise HTTPException(status_code=404, detail="Hydraulics case not found")
        return HydraulicsCaseDetail(**case)

    def delete_case(self, case_id: int) -> bool:
        database = self._require_database()
        deleted = database.delete_hydraulics_case(case_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Hydraulics case not found")
        return True

    def _require_database(self) -> DatabaseRepository:
        if self.database is None:
            raise HTTPException(status_code=500, detail="Hydraulics storage is unavailable")
        return self.database
