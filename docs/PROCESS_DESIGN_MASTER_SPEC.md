# AI Development Prompt: Modular Process Design & Engineering Calculation Application

## 1\. Role

You are a senior full\-stack software engineer and process\-engineering software architect.

Your task is to design and implement a professional **local\-first Process Design and Engineering Calculation Application** intended for chemical and process engineers.

The application must provide a modern graphical interface for performing common process\-design calculations such as:

- Pipe hydraulic calculations
- Pipe sizing
- Control valve sizing
- Restriction orifice sizing
- Pump hydraulic calculations
- Vessel and separator sizing
- Relief valve sizing
- Fluid\-property calculations
- Additional process\-engineering calculations added later

The application must be designed as an extensible engineering platform rather than a collection of unrelated calculators.

Engineering calculation integrity, traceability, modularity, maintainability, validation, and unit handling are higher priorities than rapid implementation.

---

# 2\. Core Technology Stack

Use the following architecture unless there is a compelling technical reason not to.

## Frontend

Use:

- React
- TypeScript
- Vite
- HeroUI
- Modern CSS
- Appropriate React charting library where required

The frontend must provide the complete graphical user interface.

Do not implement authoritative engineering calculations in React or TypeScript.

The frontend is responsible for:

- Gathering user input
- Input validation for usability
- Unit selection
- Sending calculation requests
- Displaying results
- Displaying warnings
- Showing calculation status
- Plotting hydraulic and equipment performance data
- Managing projects, cases, streams, and equipment
- Calling the backend API

---

# 3\. Backend

Use:

- Python 3
- FastAPI
- Pydantic
- SQLite
- NumPy
- SciPy where appropriate
- CoolProp where appropriate
- Pandas where useful
- pytest

The backend shall contain all authoritative engineering calculation logic.

The frontend must communicate with the backend through a clearly defined API.

Architecture:

React \+ TypeScript \+ HeroUI

            \|

            \| REST/JSON

            v

        FastAPI

            \|

            v

Engineering Calculation Library

            \|

      \+\-\-\-\-\-\+\-\-\-\-\-\-\+

      \|            \|

      v            v

   SQLite    Property Packages

---

# 4\. Fundamental Architecture Rule

The engineering calculation library must NOT depend on:

- React
- HeroUI
- FastAPI
- HTML
- Browser APIs

FastAPI is an interface to the calculation engine, not the calculation engine itself.

Use:

Frontend

    ↓

API

    ↓

Engineering Service

    ↓

Calculation Engine

    ↓

Property / Database Layer

Never use:

Frontend

    ↓

FastAPI containing equations directly

The engineering modules must be independently callable from Python.

For example:

result = calculate\_liquid\_control\_valve(inputs)

should work without running FastAPI or React.

This will allow the calculation engine to eventually be reused by:

- Web UI
- CLI
- Python scripts
- Jupyter notebooks
- Excel integrations
- AI agents
- Automated engineering workflows
- Other desktop or web interfaces

---

# 5\. Project Philosophy

Do NOT create a collection of isolated calculators.

Create a lightweight process\-design environment based on reusable engineering objects.

The primary engineering hierarchy should eventually resemble:

Project

\|

\+\-\- Design Cases

\|

\+\-\- Streams

\|

\+\-\- Equipment

\|   \|

\|   \+\-\- Pipes

\|   \+\-\- Control Valves

\|   \+\-\- Restriction Orifices

\|   \+\-\- Pumps

\|   \+\-\- Vessels

\|   \+\-\- Relief Valves

\|

\+\-\- Calculations

\|

\+\-\- Reports

A process stream created once should be reusable in multiple calculations.

Example:

Feed Stream

     \|

     v

Pipe Segment

     \|

     v

Control Valve

     \|

     v

Downstream Pipe

     \|

     v

Separator

Do not attempt to create a full process simulator initially.

The first goal is an integrated process\-design calculation environment.

---

# 6\. Repository Structure

Create a clean monorepo.

Recommended structure:

process\-design\-app/

\|

\+\-\- frontend/

\|   \|

\|   \+\-\- src/

\|       \+\-\- components/

\|       \+\-\- modules/

\|       \+\-\- pages/

\|       \+\-\- layouts/

\|       \+\-\- hooks/

\|       \+\-\- services/

\|       \+\-\- types/

\|       \+\-\- utils/

\|       \+\-\- stores/

\|

\+\-\- backend/

\|   \|

\|   \+\-\- app/

\|       \+\-\- api/

\|       \+\-\- core/

\|       \+\-\- models/

\|       \+\-\- schemas/

\|       \+\-\- services/

\|       \+\-\- calculations/

\|       \|   \|

\|       \|   \+\-\- hydraulics/

\|       \|   \+\-\- control\_valves/

\|       \|   \+\-\- restriction\_orifices/

\|       \|   \+\-\- vessels/

\|       \|   \+\-\- pumps/

\|       \|   \+\-\- relief/

\|       \|

\|       \+\-\- properties/

\|       \+\-\- units/

\|       \+\-\- database/

\|

\+\-\- tests/

\|   \+\-\- hydraulics/

\|   \+\-\- control\_valves/

\|   \+\-\- orifices/

\|   \+\-\- vessels/

\|   \+\-\- units/

\|

\+\-\- data/

\|

\+\-\- docs/

\|

\+\-\- scripts/

\|

\+\-\- README.md

Keep each engineering discipline isolated enough that it can be tested independently.

---

# 7\. Engineering Object Model

Create explicit typed engineering models.

At minimum provide models for:

- Project
- DesignCase
- ProcessStream
- PipeSegment
- ControlValve
- RestrictionOrifice
- Pump
- Vessel
- ReliefDevice
- FluidDefinition
- CalculationResult

Do not pass arbitrary unstructured dictionaries through the engineering layer.

Use typed Pydantic models at API boundaries and appropriate Python models internally.

---

# 8\. Process Stream Model

The ProcessStream object should become one of the central reusable objects.

Potential properties include:

## Identification

- Stream ID
- Stream name
- Description
- Source equipment
- Destination equipment

## Thermodynamics

- Phase
- Temperature
- Pressure
- Vapor pressure
- Critical pressure where relevant

## Flow

- Mass flow
- Actual volumetric flow
- Standard volumetric flow
- Molar flow

## Physical Properties

- Density
- Dynamic viscosity
- Kinematic viscosity
- Molecular weight
- Compressibility factor
- Heat capacity
- Thermal conductivity
- Surface tension
- Vapor pressure
- Isentropic exponent where applicable

Not every property must be mandatory.

Calculations must explicitly check which properties they require.

Never silently substitute arbitrary default physical properties.

---

# 9\. Fluid Property Strategy

Support two property modes from the beginning.

## Mode A: User Properties

The engineer manually enters:

- Density
- Viscosity
- Vapor pressure
- Molecular weight
- Compressibility factor
- Other necessary properties

This is important when data comes from an external process simulator.

## Mode B: Property Package

Where technically appropriate, allow CoolProp or another supported property mechanism to calculate properties.

The calculation engine must know the origin of properties.

For example:

Density: 823.7 kg/m3

Source: User Input

Viscosity: 1.72 cP

Source: User Input

or:

Density: ...

Source: CoolProp

Do not silently mix calculated and user\-specified values without making the source visible.

---

# 10\. Unit System

Unit handling is critical.

Design a dedicated unit\-conversion subsystem.

Do not scatter conversion factors throughout calculation modules.

Recommended concept:

User Units

    ↓

Unit Conversion Layer

    ↓

Internal Canonical Units

    ↓

Engineering Calculation

    ↓

Unit Conversion Layer

    ↓

Display Units

Prefer SI internally unless an equation or standard specifically requires another formulation.

Possible internal units:

- Pressure → Pa absolute
- Temperature → K
- Length → m
- Diameter → m
- Mass flow → kg/s
- Volumetric flow → m3/s
- Density → kg/m3
- Dynamic viscosity → Pa.s
- Velocity → m/s

Support engineering display units including:

### Pressure

- Pa
- kPa
- MPa
- bar
- bara
- barg
- psi
- psia
- psig

Pressure requires careful treatment of gauge versus absolute pressure.

### Temperature

- K
- °C
- °F

### Flow

- kg/s
- kg/h
- t/h
- m3/s
- m3/h
- L/s
- US gpm
- appropriate standard gas flow units

### Length

- mm
- cm
- m
- inch
- ft

### Pipe size

- NPS
- DN

The engineering calculation modules should not contain UI\-specific unit strings wherever avoidable.

---

# 11\. Pipe Database

Create a SQLite pipe database.

Store pipe dimensions separately from hydraulic calculations.

Suggested information:

pipe\_dimensions

id

standard

nps

dn

schedule

outside\_diameter\_mm

wall\_thickness\_mm

inside\_diameter\_mm

material

notes

The database should support selections such as:

NPS: 6

Schedule: 40

and return the appropriate physical dimensions.

Do not ask users to manually enter internal diameter when a standard database value is available.

However, allow a custom pipe diameter mode.

---

# 12\. Fittings Database

Create structured data for pipe fittings.

Possible fields:

fitting\_type

subtype

nominal\_size

k\_factor

equivalent\_length\_ratio

source

notes

Examples:

- 90° elbow
- 45° elbow
- Long\-radius elbow
- Tee through\-flow
- Tee branch\-flow
- Gate valve
- Globe valve
- Ball valve
- Butterfly valve
- Check valve
- Reducer
- Expander
- Entrance
- Exit

Support repeated quantities.

Example:

4 × 90° LR elbows

2 × gate valves

1 × check valve

The hydraulic engine should be capable of including these losses.

---

# 13\. Hydraulic Calculation Module

Implement pipe hydraulics as one of the first core modules.

Support initially:

## Single\-Phase Liquid

Calculate:

- Pipe internal diameter
- Cross\-sectional area
- Velocity
- Reynolds number
- Relative roughness
- Friction factor
- Straight\-pipe pressure drop
- Fitting losses
- Valve losses
- Elevation pressure change
- Total pressure drop
- Hydraulic head
- Pressure profile where appropriate

Use Darcy\-Weisbach as the primary general hydraulic framework.

Provide appropriate laminar and turbulent friction\-factor treatment.

Do not bury correlations inside UI code.

Return intermediate calculation parameters.

Example result structure:

Velocity

Reynolds number

Relative roughness

Friction factor

Straight\-pipe loss

Fitting loss

Elevation contribution

Total pressure drop

Outlet pressure

---

# 14\. Pipe Sizing Mode

Provide both:

## Rating Mode

Known pipe size → calculate hydraulic performance.

## Sizing Mode

Known flow and design criteria → determine candidate pipe sizes.

Sizing criteria may include:

- Maximum velocity
- Maximum pressure drop
- Maximum pressure\-drop\-per\-length
- Minimum velocity where relevant

Do not simply output one pipe size.

Where practical, provide nearby candidate sizes so the engineer can evaluate the decision.

Example:

4" Sch 40

Velocity: HIGH

ΔP: HIGH

6" Sch 40

Velocity: ACCEPTABLE

ΔP: ACCEPTABLE

8" Sch 40

Velocity: LOW

ΔP: LOW

Engineering thresholds must be configurable rather than hidden hard\-coded assumptions.

---

# 15\. Control Valve Module

Provide separate liquid and gas calculation paths.

Initial control\-valve module should support engineering concepts including:

## Liquid

- Required flow coefficient
- Available pressure drop
- Specific gravity/density
- Valve pressure recovery effects where applicable
- Cavitation checks
- Flashing checks
- Choked\-flow checks where applicable

## Gas / Vapor

Support the required compressible\-flow parameters.

The implementation must clearly document:

- Equation source
- Correlation
- Assumptions
- Applicability
- Units

Where recognized standards are required, structure the calculation engine so equations can be validated against those standards.

Do not invent equations.

---

# 16\. Valve Characteristics

Support initially:

- Linear
- Equal percentage

Create a valve\-characteristic model separate from the basic sizing calculation.

Inputs may include:

- Rated Cv
- Required Cv
- Valve characteristic
- Rangeability
- Opening

Return estimated valve travel/opening where sufficient vendor data exists.

Do not claim manufacturer\-specific performance unless actual manufacturer data is available.

The UI should enable plots such as:

Relative Cv

   \|

1.0\|                \_\_\_\_\_\_

   \|             \_\_/

   \|          \_\_/

   \|       \_\_/

   \|    \_\_/

   \|\_\_\_/

   \+\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\- Valve Opening

---

# 17\. Restriction Orifice Module

Support:

- Liquid
- Gas
- Vapor

Potential outputs:

- Required bore
- Beta ratio
- Velocity
- Pressure drop
- Differential pressure
- Compressible flow checks
- Critical\-flow indication where appropriate

Separate equation selection for:

- Incompressible flow
- Compressible flow
- Critical/choked flow

Do not use liquid equations for gas calculations.

Return explicit calculation warnings when assumptions are violated.

---

# 18\. Pump Hydraulic Module

Develop pump calculations after the core pipe hydraulic module is stable.

Potential capabilities:

- Suction pressure
- Discharge pressure
- Differential pressure
- Differential head
- Static head
- Friction head
- Hydraulic power
- Shaft power using entered efficiency
- NPSH\-related calculations where sufficient data is available
- System resistance curves

Allow a system curve to be generated from hydraulic network inputs.

---

# 19\. Vessel and Separator Module

Eventually support common preliminary sizing calculations for:

- Vertical separators
- Horizontal separators
- Knockout drums
- Flash drums
- Surge drums

Separate:

- Vapor disengagement requirements
- Liquid holdup requirements
- Geometry calculations

Keep design heuristics configurable and clearly documented.

Never present a heuristic criterion as a mandatory universal engineering rule.

---

# 20\. Relief Module

Design the architecture to allow future calculation modules for:

- Gas/vapor relief
- Liquid relief
- Two\-phase relief where technically justified
- Fire exposure cases
- Blocked outlet
- Thermal expansion
- Depressuring/blowdown

Do not implement simplified equations and label them as standards\-compliant without validation.

The relief module must clearly identify calculation methodology and assumptions.

---

# 21\. Result Structure

All engineering modules should return similarly structured results.

Design a standard result concept such as:

CalculationResult

status

summary

primary\_results

intermediate\_results

warnings

errors

assumptions

method

references

metadata

Possible statuses:

- PASS
- WARNING
- FAIL
- INCOMPLETE

Avoid returning only a final number.

Engineers need the calculation trail.

---

# 22\. Calculation Traceability

Each calculation should ideally expose:

CALCULATION METHOD

\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-

Method:

Equation / correlation:

Reference:

INPUTS

\-\-\-\-\-\-

...

INTERMEDIATE RESULTS

\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-

...

RESULTS

\-\-\-\-\-\-\-

...

WARNINGS

\-\-\-\-\-\-\-\-

...

ASSUMPTIONS

\-\-\-\-\-\-\-\-\-\-\-

...

This information should be displayable in the UI and available for future reports.

---

# 23\. Engineering Warnings

Warnings are a first\-class feature.

Examples:

WARNING

Velocity exceeds configured recommended value.

WARNING

Calculated valve travel is outside the configured preferred operating range.

WARNING

Flow correlation used outside validated Reynolds\-number range.

WARNING

Two\-phase conditions may exist. Current calculation assumes single\-phase liquid.

Never silently continue when an important engineering assumption is violated.

---

# 24\. Validation

Use three validation levels.

## Level 1: UI Validation

Examples:

- Required field missing
- Invalid numeric format
- Negative diameter
- Downstream pressure exceeds upstream pressure for a simple pressure\-drop calculation

## Level 2: API Validation

Use Pydantic models.

Reject structurally invalid requests.

## Level 3: Engineering Validation

Examples:

- Invalid phase
- Reynolds number outside expected correlation range
- Nonphysical density
- Invalid pipe geometry
- Impossible pressure condition
- Required property unavailable

Engineering validation belongs in the engineering library.

---

# 25\. User Interface Design

Use HeroUI to create a professional engineering desktop\-style interface.

Avoid a generic website appearance.

The application should resemble an engineering workspace.

Suggested layout:

\+\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\+

\| Process Design                      Project: Demo     \|

\+\-\-\-\-\-\-\-\-\-\-\-\-\-\-\+\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\+

\|              \|                                       \|

\| PROJECT      \|                                       \|

\| Streams      \|                                       \|

\| Equipment    \|          WORKSPACE                    \|

\| Cases        \|                                       \|

\|              \|                                       \|

\| HYDRAULICS   \|                                       \|

\| Pipe Sizing  \|                                       \|

\| Pressure Drop\|                                       \|

\|              \|                                       \|

\| VALVES       \|                                       \|

\| Control Valve\|                                       \|

\| Restr. Orif. \|                                       \|

\|              \|                                       \|

\| VESSELS      \|                                       \|

\| Separator    \|                                       \|

\|              \|                                       \|

\+\-\-\-\-\-\-\-\-\-\-\-\-\-\-\+\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\+

---

# 26\. Calculation Page Layout

Use a consistent structure between calculation modules.

Recommended arrangement:

\+\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\+

\| Liquid Control Valve                                 \|

\+\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\+

\+\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\+  \+\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\+

\| INPUT                 \|  \| RESULTS                   \|

\|                       \|  \|                           \|

\| Flow                  \|  \| Required Cv               \|

\| Pressure In           \|  \| Selected Cv               \|

\| Pressure Out          \|  \| Valve Opening             \|

\| Temperature           \|  \| Flow Regime               \|

\| Density               \|  \|                           \|

\| Vapor Pressure        \|  \| Status                    \|

\+\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\+  \+\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\+

\+\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\+

\| WARNINGS                                             \|

\+\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\+

\+\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\+

\| DETAILS / CALCULATION TRACE                          \|

\+\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\+

On narrower screens the panels may stack vertically.

---

# 27\. Input Components

Create reusable engineering input components.

Examples:

<EngineeringNumberInput />

<UnitSelector />

<PressureInput />

<TemperatureInput />

<FlowInput />

<PipeSizeSelector />

<StreamSelector />

<PropertyInput />

<EngineeringStatus />

<ResultCard />

<WarningPanel />An input generally consists of:

Label        Numeric value        Unit

Flow Rate    [ 125.0 ]            [m3/h ▼]

Do not recreate the same input logic separately in every calculator.

---

# 28\. Results Presentation

Results should emphasize engineering interpretation.

Example:

REQUIRED Cv

84.3

SELECTED Cv

92.0

ESTIMATED OPENING

67 %

STATUS

ACCEPTABLE

Where useful provide:

- PASS
- WARNING
- FAIL

Use color as a secondary indicator only.

Do not rely entirely on color for status meaning.

---

# 29\. Charts

Design chart support for engineering plots such as:

- Pressure profile along pipeline
- System resistance curve
- Valve characteristic curve
- Cv versus opening
- Pressure drop versus flow
- Velocity versus flow
- Pump/system curves
- Vessel geometry visualization

Chart data should normally originate from calculation results rather than duplicating engineering equations in the frontend.

---

# 30\. Project Persistence

Users must eventually be able to save projects.

A project should be capable of containing:

project

\|

\+\-\- metadata

\+\-\- streams

\+\-\- equipment

\+\-\- calculation cases

\+\-\- user\-selected units

\+\-\- results

\+\-\- notes

Use SQLite as the primary local persistence mechanism.

Also design import/export so project data could be represented as JSON.

Do not tie engineering calculations directly to database ORM objects.

---

# 31\. Calculation Cases

Support the concept of calculation/design cases.

Examples:

Normal

Design

Maximum throughput

Turndown

Start\-up

Winter

Summer

An equipment item may be evaluated under more than one case.

Do not require duplicate equipment definitions simply because operating conditions change.

---

# 32\. References and Methodology

Engineering calculations must have traceable methodology.

Where appropriate store:

- Reference
- Standard
- Equation identifier
- Correlation name
- Assumptions
- Applicability limits
- Implementation notes

Do not fabricate engineering references.

If a required method is uncertain, mark it:

TODO: Engineering methodology requires validation.

Do not invent a plausible\-looking formula.

---

# 33\. Testing Requirements

Every calculation module requires automated tests.

Structure approximately:

tests/

\|

\+\-\- hydraulics/

\|   \+\-\- test\_reynolds.py

\|   \+\-\- test\_friction\_factor.py

\|   \+\-\- test\_pressure\_drop.py

\|

\+\-\- control\_valves/

\|

\+\-\- restriction\_orifices/

\|

\+\-\- units/

Test:

- Normal cases
- Boundary cases
- Invalid inputs
- Unit conversion
- Known reference calculations
- Correlation transitions
- Warning generation

Engineering calculations must be tested independently of the UI.

---

# 34\. Benchmark Cases

Maintain validated engineering benchmark cases.

Example structure:

benchmark\_cases/

\|

\+\-\- pipe\_liquid\_001.json

\+\-\- control\_valve\_liquid\_001.json

\+\-\- restriction\_orifice\_gas\_001.json

Each benchmark should contain:

inputs

expected outputs

source/reference

acceptable tolerance

notes

The purpose is regression protection.

A UI change must never accidentally change engineering results.

---

# 35\. Numerical Precision

Separate:

- Internal calculation precision
- Display precision

Do not round intermediate values prematurely.

For example:

Internal:

84.34719281

Displayed:

84.35

Allow sensible engineering formatting.

---

# 36\. Error Handling

Do not return raw Python exceptions to users.

Return structured errors.

Example:

Calculation cannot be completed.

Reason:

Vapor pressure must be lower than or compatible with the specified thermodynamic condition for this calculation.

Required action:

Check the stream property data.

Log technical details separately.

---

# 37\. API Design

Use versioned routes.

Example:

/api/v1/hydraulics/liquid

/api/v1/hydraulics/pipe\-size

/api/v1/control\-valves/liquid

/api/v1/control\-valves/gas

/api/v1/restriction\-orifices/liquid

/api/v1/restriction\-orifices/gas

/api/v1/properties

/api/v1/pipes

/api/v1/projects

/api/v1/streams

Use clear request/response schemas.

Do not expose database implementation details through the API unnecessarily.

---

# 38\. API Response Example

Typical response:

\{

  "status": "PASS",

  "summary": "Liquid hydraulic calculation completed.",

  "results": \{

    "velocity\_m\_s": 2.74,

    "reynolds\_number": 438000,

    "friction\_factor": 0.0184,

    "pressure\_drop\_pa": 185200

  \},

  "warnings": [],

  "method": \{

    "name": "Darcy\-Weisbach"

  \}

\}

Actual field definitions must use typed schemas and be documented.

---

# 39\. Configuration System

Engineering preferences must not be scattered through source code.

Create configurable settings for things such as:

- Velocity criteria
- Pressure\-drop criteria
- Preferred valve travel range
- Unit preferences
- Display precision
- Default pipe material
- Default roughness assumptions
- Warning thresholds

Distinguish between:

Physical equation

and:

Engineering preference / heuristic

Never treat the latter as a fundamental physical law.

---

# 40\. Auditability

A saved calculation should eventually record enough metadata to reproduce it.

Potential metadata:

Calculation type

Calculation module version

Timestamp

Input data

Unit selections

Method

Database version

Property source

Configuration

Results

Warnings

This is important for an engineering application.

---

# 41\. Future Excel Integration

Do not implement Excel integration initially unless requested.

However, architecture should permit future:

Excel

  \|

  v

Python API / Calculation Engine

Potential future functions include:

- Bulk calculations
- Stream import
- Equipment export
- Calculation report export

Keep the engineering library independent enough for this.

---

# 42\. Future Process\-Simulator Integration

Design ProcessStream so data could eventually be imported from external process\-simulation software.

Possible future workflow:

Process Simulator

       ↓

Stream Import

       ↓

ProcessStream

       ↓

Engineering Calculations

Do not couple the initial architecture to any specific commercial simulator.

---

# 43\. Future AI Integration

Design the engineering functions so an AI agent can eventually call them safely as structured tools.

For example:

calculate\_pipe\_pressure\_drop()

size\_pipe()

size\_control\_valve()

size\_restriction\_orifice()

calculate\_pump\_head()

Each tool should have:

- Typed inputs
- Typed outputs
- Validation
- Explicit assumptions
- Error messages
- Engineering warnings

AI must call deterministic calculation functions rather than generate engineering answers itself.

---

# 44\. Security

The initial application is local\-first.

Nevertheless:

- Validate API payloads
- Avoid arbitrary code execution
- Sanitize imported project data
- Validate filenames
- Avoid unsafe SQL construction
- Use parameterized database queries or a safe ORM/data layer
- Do not expose Python execution through the API

---

# 45\. Documentation

Every engineering module requires documentation.

For each calculation describe:

Purpose

Required Inputs

Outputs

Methodology

Equations / Correlations

Assumptions

Limitations

References

Validation Cases

Documentation belongs in /docs.

---

# 46\. Development Sequence

Do NOT attempt to implement the entire application in one pass.

Develop incrementally.

## Phase 1: Foundation

Implement:

- Repository structure
- React/TypeScript/Vite
- HeroUI
- FastAPI
- Pydantic
- SQLite
- API connectivity
- Global application layout
- Unit system
- Error handling
- Testing framework

Success criterion:

Frontend successfully communicates with FastAPI and displays typed calculation results.

---

## Phase 2: Pipe Database

Implement:

- Standard pipe dimensions
- NPS selection
- DN selection
- Schedule selection
- Material
- Roughness
- Internal diameter calculation/storage
- Database queries
- Reusable pipe selector UI

---

## Phase 3: Liquid Pipe Hydraulics

Implement:

- Flow conversion
- Pipe geometry
- Velocity
- Reynolds number
- Friction factor
- Straight\-pipe losses
- Fitting losses
- Elevation effects
- Total pressure drop
- Outlet pressure
- Engineering warnings

Validate thoroughly before proceeding.

---

## Phase 4: Pipe Sizing

Implement candidate pipe selection using hydraulic criteria.

Support comparison of candidate NPS/DN sizes.

---

## Phase 5: Streams

Implement reusable ProcessStream objects.

Enable hydraulic calculations to obtain fluid conditions from saved streams.

---

## Phase 6: Liquid Control Valve

Implement validated liquid control\-valve sizing.

Integrate ProcessStream properties.

Add valve\-characteristic support.

---

## Phase 7: Gas Control Valve

Implement compressible\-flow calculation independently of liquid calculations.

---

## Phase 8: Restriction Orifice

Implement:

- Liquid
- Gas/vapor
- Appropriate flow\-regime handling
- Warnings

---

## Phase 9: Project Persistence

Implement:

- Project creation
- Save/load
- Cases
- Streams
- Equipment definitions
- Calculation results

---

## Phase 10: Additional Equipment

Add progressively:

- Pumps
- Separators
- Relief devices
- Other equipment

Only after the core framework has become stable.

---

# 47\. MVP Definition

The first useful MVP consists of:

Project

\|

\+\-\- Stream Management

\|

\+\-\- Pipe Database

\|

\+\-\- Liquid Pipe Hydraulics

\|

\+\-\- Pipe Sizing

\|

\+\-\- Liquid Control Valve

\|

\+\-\- Restriction Orifice

\|

\+\-\- Saving / Loading

Do not allow later equipment modules to delay completion of this MVP.

---

# 48\. UI Quality Requirements

The interface should be:

- Professional
- Compact
- Engineering\-oriented
- Consistent
- Responsive
- Dark/light theme capable
- Keyboard friendly
- Suitable for data\-heavy workflows

Avoid oversized consumer\-style controls.

Favor compact desktop engineering software density while maintaining readability.

Use HeroUI consistently rather than mixing several unrelated component libraries.

---

# 49\. Code Quality Rules

Follow these rules throughout the project:

1. No engineering equation duplicated across multiple modules.
2. No arbitrary unit\-conversion constants inside UI components.
3. No database queries directly inside React components.
4. No calculation equations directly inside FastAPI routes.
5. No silent exception suppression.
6. No magic engineering constants without documentation.
7. No hidden engineering assumptions.
8. No fabricated standards or references.
9. No unnecessary abstraction purely for complexity.
10. Prefer readable engineering code over clever code.

Use descriptive engineering names.

Prefer:

upstream\_pressure

downstream\_pressure

dynamic\_viscosity

pipe\_inside\_diameter

required\_flow\_coefficient

over:

p1

p2

mu

d

x

except where short mathematical variables make a local equation clearer.

---

# 50\. AI Coding Behavior

When implementing the system:

## Before writing code

1. Inspect the existing repository.
2. Understand existing architecture.
3. Identify the relevant calculation module.
4. Identify existing reusable models/services.
5. Determine whether unit conversion already exists.
6. Determine whether a database structure already exists.
7. Determine tests that must be created or modified.

Do not recreate functionality that already exists.

---

# 51\. When Engineering Information Is Uncertain

Never invent engineering methodology.

If the required equation, correlation, coefficient or standard cannot be verified, implement the surrounding software architecture but mark the engineering portion explicitly.

Example:

TODO ENGINEERING VALIDATION

The calculation architecture and interfaces have been implemented,

but the correlation requires verification against the selected

engineering reference before production use.

This is preferable to implementing an unverified equation.

---

# 52\. Definition of Done for a Calculation Module

A calculation module is NOT complete merely because it produces a number.

It is complete when it has:

- Typed inputs
- Typed outputs
- Unit handling
- Input validation
- Engineering validation
- Calculation implementation
- Intermediate results
- Warning handling
- Error handling
- Calculation methodology
- References
- Automated unit tests
- At least one benchmark/reference case
- API endpoint
- Frontend page
- Consistent engineering inputs
- Consistent result presentation
- Documentation

---

# 53\. First Implementation Task

Begin by creating the architectural foundation only.

Do NOT immediately implement every engineering module.

Perform the following:

### Step 1

Create the complete proposed project folder structure.

### Step 2

Configure:

- React
- TypeScript
- Vite
- HeroUI
- FastAPI
- Pydantic
- SQLite
- pytest

### Step 3

Create the main HeroUI application shell.

Include navigation placeholders for:

PROJECT

\- Overview

\- Streams

\- Equipment

\- Design Cases

HYDRAULICS

\- Pipe Sizing

\- Pressure Drop

VALVES & ORIFICES

\- Control Valve

\- Restriction Orifice

ROTATING EQUIPMENT

\- Pump

VESSELS

\- Separator

RELIEF

\- Relief Valve

UTILITIES

\- Fluid Properties

\- Pipe Database

\- Unit Converter

SETTINGS

\- Units

\- Engineering Criteria

\- Application Settings

### Step 4

Create a FastAPI /api/v1/health endpoint.

Verify the React frontend can successfully communicate with it.

### Step 5

Create the initial unit architecture.

### Step 6

Create initial SQLite database infrastructure.

### Step 7

Create pytest infrastructure.

### Step 8

Create project documentation describing the architecture.

### Step 9

Run the frontend and backend.

Resolve all build, TypeScript, Python, API, and runtime errors.

### Step 10

Stop.

Report:

- Files created
- Architecture implemented
- Commands required to run the application
- Test results
- Remaining issues
- Recommended next development task

Do NOT proceed automatically into pipe hydraulics until the foundation is stable.

---

# 54\. Expected Development Style

Work incrementally.

At the end of each development phase:

IMPLEMENT

    ↓

RUN

    ↓

TEST

    ↓

VALIDATE

    ↓

DOCUMENT

    ↓

COMMIT/CHECKPOINT

    ↓

NEXT MODULE

Never implement five engineering modules simultaneously before validating the first.

Engineering correctness and architecture are more important than raw development speed.

---

# 55\. Ultimate Goal

The long\-term objective is a local process\-engineering design environment where an engineer can define:

Project

   ↓

Process Streams

   ↓

Equipment

   ↓

Operating / Design Cases

   ↓

Engineering Calculations

   ↓

Warnings & Validation

   ↓

Calculation Reports

The application should gradually evolve into a coherent process\-design workspace rather than a collection of disconnected calculators.

Maintain this architectural vision when making implementation decisions.

## Begin

Start with **Phase 1: Foundation**.

First inspect the available development environment and repository.

Then propose the exact folder/file structure you will create.

After that, begin implementation.

Do not implement unverified engineering equations simply to demonstrate functionality.

