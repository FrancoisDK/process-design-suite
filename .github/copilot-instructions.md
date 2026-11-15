# Process Design Suite - Copilot Instructions

## Project Purpose

This repository contains a local-first professional process engineering design and calculation application.

The application is intended for chemical and process engineering calculations including:

- Pipe hydraulics
- Pipe sizing
- Control valve sizing
- Restriction orifice sizing
- Process stream management
- Pipe and fittings databases

Future modules may include:

- Pump hydraulics
- Compressors
- Separator sizing
- Vessel sizing
- Relief valve sizing
- Blowdown and depressuring
- Heat transfer calculations
- Fluid property calculations

The authoritative project specification is:

`docs/PROCESS_DESIGN_MASTER_SPEC.md`

Read the relevant sections of that specification before making architectural or engineering changes.

---

# Architecture

Use the following architecture:

Frontend:
React + TypeScript + Vite + HeroUI

API:
FastAPI + Pydantic

Engineering calculation engine:
Python

Database:
SQLite

Testing:
pytest for Python engineering code

The architecture is:

Frontend
    |
    v
FastAPI
    |
    v
Engineering Service Layer
    |
    v
Python Calculation Engine
    |
    +--- Units
    +--- Fluid Properties
    +--- Engineering Reference Data
    +--- SQLite Persistence

---

# Engineering Calculation Authority

Python is the authoritative engineering calculation engine.

Do NOT implement authoritative engineering equations in:

- React
- TypeScript
- HeroUI components
- frontend services
- FastAPI route handlers
- database code

React collects input and displays results.

FastAPI exposes typed API endpoints.

Python engineering modules perform calculations.

Engineering calculation functions must remain independently callable without running React or FastAPI.

---

# FastAPI Rules

FastAPI routes must remain thin.

Preferred structure:

API Route
    -> Service
        -> Engineering Calculation

Do not place large engineering calculation implementations directly inside API route functions.

Use Pydantic models for API request and response structures.

Return structured engineering results rather than unstructured dictionaries where practical.

---

# Frontend Rules

Use:

- React
- TypeScript
- Vite
- HeroUI

Maintain a professional engineering desktop-style interface.

Prefer:

- Compact controls
- High information density
- Clearly grouped engineering inputs
- Tables
- Tabs
- Cards
- Tooltips
- Accordions
- Searchable selectors
- Explicit engineering status indicators

Avoid:

- Marketing-site layouts
- Excessive whitespace
- Oversized controls
- Decorative animation
- Consumer-style interfaces

Do not duplicate engineering calculations in TypeScript.

---

# Unit Handling

Engineering unit handling is a dedicated subsystem.

Never scatter unit conversion constants throughout the application.

Use the pattern:

User Units
    -> Conversion Layer
    -> Canonical Internal Units
    -> Engineering Calculation
    -> Conversion Layer
    -> Display Units

Prefer SI canonical units internally where technically appropriate.

Examples:

Pressure:
Pa absolute

Temperature:
K

Length:
m

Mass flow:
kg/s

Actual volumetric flow:
m3/s

Density:
kg/m3

Dynamic viscosity:
Pa.s

Velocity:
m/s

Pressure calculations must explicitly distinguish ABSOLUTE pressure from GAUGE pressure.

Never treat bara and barg or psia and psig as simple scaling conversions.

---

# Engineering Integrity

Engineering correctness has priority over implementation speed.

NEVER fabricate:

- Engineering equations
- Correlations
- Coefficients
- Standards
- Equation numbers
- Vendor information
- Applicability limits
- Engineering references

If an engineering method cannot be verified, mark the implementation:

ENGINEERING VALIDATION REQUIRED

Do not substitute a plausible-looking equation.

---

# Engineering Heuristics

Distinguish between:

1. Physical equations
2. Engineering correlations
3. Engineering heuristics/preferences

Typical velocity limits, pressure-drop criteria, preferred valve travel ranges, and similar values are engineering criteria rather than physical laws.

Keep these configurable where practical.

Do not silently hard-code engineering heuristics into fundamental calculation functions.

---

# Calculation Results

Engineering calculations should normally return:

- Primary results
- Important intermediate results
- Calculation status
- Warnings
- Errors
- Assumptions
- Methodology
- References where available
- Relevant metadata

Do not return only a single final number when engineering interpretation requires additional information.

Calculation status should use consistent concepts such as:

- PASS
- WARNING
- FAIL
- INCOMPLETE

---

# Engineering Warnings

Warnings are a first-class feature.

Examples include:

- High velocity
- High pressure drop
- Correlation applicability exceeded
- Possible flashing
- Possible cavitation
- Possible two-phase conditions
- Missing required property
- Valve operating outside preferred travel

Do not silently ignore an important engineering limitation.

---

# Testing

Every engineering calculation requires automated tests.

After modifying Python engineering calculation code:

1. Run the relevant unit tests.
2. Run relevant benchmark tests.
3. Report failures.
4. Fix failures before declaring the work complete.

Do not modify tests merely to force incorrect code to pass.

Engineering benchmark cases must identify whether their expected values have been independently validated.

Never label synthetic data as validated reference data.

---

# Numerical Precision

Do not prematurely round intermediate engineering calculations.

Maintain appropriate numerical precision internally.

Apply display rounding only when presenting results to the user.

---

# Database Rules

SQLite is the primary local persistence and engineering reference database.

Database access must remain separate from engineering equations.

Use repository/service boundaries where appropriate.

Do not execute SQL directly inside React components.

Do not tightly couple engineering calculation functions to database objects.

Pass required engineering data into calculation functions through typed interfaces.

---

# Process Streams

ProcessStream is a reusable engineering object.

The architecture should allow streams to contain properties such as:

- Temperature
- Pressure
- Phase
- Mass flow
- Volumetric flow
- Density
- Viscosity
- Molecular weight
- Vapor pressure
- Compressibility
- Other required thermodynamic properties

Not every property is mandatory.

Individual calculations must explicitly validate required properties.

Never silently invent missing properties.

---

# Code Quality

Prioritize:

1. Correctness
2. Engineering clarity
3. Readability
4. Testability
5. Traceability
6. Maintainability

Use descriptive engineering names.

Prefer:

upstream_absolute_pressure
downstream_absolute_pressure
inside_diameter
dynamic_viscosity
vapor_pressure
required_cv

over ambiguous names outside localized mathematical equations.

Avoid unnecessary abstraction.

Do not create duplicate implementations of existing functionality.

---

# Existing Code

Before implementing functionality:

1. Inspect the repository.
2. Search for existing related code.
3. Understand the current architecture.
4. Reuse existing models where appropriate.
5. Reuse existing unit infrastructure.
6. Reuse existing database infrastructure.
7. Reuse existing UI components.
8. Inspect existing tests.

Do not replace working code without a clear reason.

Do not refactor unrelated functionality while implementing a focused task.

---

# Development Workflow

Work incrementally:

INSPECT
    ->
PLAN
    ->
IMPLEMENT
    ->
RUN
    ->
TEST
    ->
FIX
    ->
VALIDATE
    ->
DOCUMENT

Do not attempt multiple major engineering modules simultaneously.

Complete the requested development phase before moving to another phase.

---

# Browser/UI Validation

Playwright MCP is available.

After significant frontend changes:

1. Start the required frontend/backend development servers.
2. Use Playwright to open the application.
3. Exercise the affected workflow.
4. Check that inputs and navigation function correctly.
5. Check calculation result presentation.
6. Check engineering warning presentation.
7. Check for obvious runtime/browser errors.

Do not declare significant UI work complete solely because TypeScript compiles.

---

# Git and Change Discipline

Keep changes focused.

Before large changes, inspect Git status and existing implementation.

Do not remove unrelated files.

Do not overwrite working modules unnecessarily.

Do not commit generated secrets, credentials, tokens, environment variables, databases containing sensitive data, or development artifacts.

---

# Project Specification

`docs/PROCESS_DESIGN_MASTER_SPEC.md` is the authoritative product and architecture specification.

When a user request conflicts with an existing implementation:

1. Inspect the specification.
2. Inspect existing code.
3. Identify the conflict.
4. Prefer the explicit current user request when intentional.
5. Avoid silently changing project architecture.

---

# Development Phases

Follow the development phases defined in:

`docs/PROCESS_DESIGN_MASTER_SPEC.md`

Do not automatically proceed to a subsequent phase after completing the requested phase.

At the end of a development phase report:

- Files created
- Files modified
- Architecture implemented
- Tests executed
- Test results
- Build results
- Remaining issues
- Engineering items requiring validation
- Recommended next step

---

# Current Priority

Establish a clean and reliable application foundation before implementing engineering calculations.

The initial foundation includes:

- React
- TypeScript
- Vite
- HeroUI
- FastAPI
- Pydantic
- SQLite infrastructure
- Unit architecture
- pytest
- Frontend/backend communication
- Application navigation shell
- Playwright frontend verification

Do not implement unverified process engineering equations merely to populate the UI.