# Process Design Suite

## Phase 3 backend bootstrap: liquid pipe hydraulics

The backend now exposes an initial hydraulics endpoint:

- `POST /api/v1/hydraulics/liquid-pipe`
- `POST /api/v1/hydraulics/gas-pipe/low-dp`
- `POST /api/v1/hydraulics/gas-pipe/high-dp`
- `GET/POST /api/v1/hydraulics/cases` and `GET/DELETE /api/v1/hydraulics/cases/{id}` for saved cases

This first slice includes:

- velocity, Reynolds number, friction factor, and straight-pipe pressure drop
- optional elevation pressure drop
- optional fittings pressure drop using total K (`fittings_method: "k_total"`)
- Darby 3K fittings support (`fittings_method: "3k"`) with per-fitting entries:
  - `k1`, `k_inf`, `k_d`, and `quantity`
  - effective K calculated as `K = k1/Re + k_inf * (1 + k_d / D_in^0.3)`
- gas hydraulics split into:
  - low-ΔP model for moderate compressibility effects
  - high-ΔP/high-Mach screening model with critical-pressure-ratio choking check