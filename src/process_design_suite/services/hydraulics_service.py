from __future__ import annotations

from process_design_suite.engine.pipe_hydraulics import calculate_liquid_pipe_hydraulics
from process_design_suite.schemas.hydraulics import LiquidPipeHydraulicsInput, LiquidPipeHydraulicsResult


class HydraulicsService:
    def calculate_liquid_pipe_hydraulics(
        self, inputs: LiquidPipeHydraulicsInput
    ) -> LiquidPipeHydraulicsResult:
        return calculate_liquid_pipe_hydraulics(inputs)
