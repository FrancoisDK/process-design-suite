from __future__ import annotations

from process_design_suite.engine.pipe_hydraulics import (
    calculate_gas_pipe_hydraulics_high_dp,
    calculate_gas_pipe_hydraulics_low_dp,
    calculate_liquid_pipe_hydraulics,
)
from process_design_suite.schemas.hydraulics import (
    GasPipeHydraulicsHighDPInput,
    GasPipeHydraulicsHighDPResult,
    GasPipeHydraulicsLowDPInput,
    GasPipeHydraulicsLowDPResult,
    LiquidPipeHydraulicsInput,
    LiquidPipeHydraulicsResult,
)


class HydraulicsService:
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
