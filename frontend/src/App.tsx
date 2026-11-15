import { useEffect, useState } from 'react'
import { Button, Card, Chip } from '@heroui/react'
import './App.css'

type DatabaseHealth = {
  type: string
  status: string
  database_path: string
  message?: string | null
}

type HealthResponse = {
  status: 'ok' | 'degraded'
  service: string
  version: string
  environment: string
  timestamp: string
  database: DatabaseHealth
  readiness: 'ready' | 'not_ready'
}

type PipeRecord = {
  id: number
  nominal_size: string
  dn_size: string
  schedule: string
  material: string
  outside_diameter_in: number
  wall_thickness_in: number
  inside_diameter_in: number
  roughness_mm: number | null
  standard: string
}

type PipeCatalogOptions = {
  nominal_sizes: string[]
  dn_sizes: string[]
  schedules: string[]
  materials: string[]
}

type DisplayUnit = 'mm' | 'in'
type DecimalPlaces = 2 | 3 | 4
type PressureUnit = 'kPa' | 'bar' | 'psia'
type PressureProfileId = 'sea-level' | '500m' | '1000m' | '1500m' | '2000m' | 'custom'
type HydraulicsModel = 'liquid' | 'gas-low-dp' | 'gas-high-dp'

const ALL_FILTER_OPTION = 'All'
const INCH_TO_MM = 25.4
const DISPLAY_UNIT_STORAGE_KEY = 'process-design-suite.display-unit'
const DISPLAY_PRECISION_STORAGE_KEY = 'process-design-suite.display-precision'
const PRESSURE_UNIT_STORAGE_KEY = 'process-design-suite.pressure-unit'
const PRESSURE_PROFILE_STORAGE_KEY = 'process-design-suite.pressure-profile'
const ATM_PRESSURE_STORAGE_KEY = 'process-design-suite.atm-pressure-kpa'
const STANDARD_SEA_LEVEL_PRESSURE_KPA = 101.325
const PRESSURE_PROFILES: Array<{ id: PressureProfileId; label: string; elevationM: number | null; pressureKpa: number }> = [
  { id: 'sea-level', label: 'Sea level (~0 m)', elevationM: 0, pressureKpa: 101.325 },
  { id: '500m', label: 'Elevation ~500 m', elevationM: 500, pressureKpa: 95.460 },
  { id: '1000m', label: 'Elevation ~1000 m', elevationM: 1000, pressureKpa: 89.875 },
  { id: '1500m', label: 'Elevation ~1500 m', elevationM: 1500, pressureKpa: 84.560 },
  { id: '2000m', label: 'Elevation ~2000 m', elevationM: 2000, pressureKpa: 79.500 },
  { id: 'custom', label: 'Custom local pressure', elevationM: null, pressureKpa: STANDARD_SEA_LEVEL_PRESSURE_KPA },
]

const isDisplayUnit = (value: string | null): value is DisplayUnit => value === 'mm' || value === 'in'
const isDecimalPlaces = (value: string | null): value is `${DecimalPlaces}` => value === '2' || value === '3' || value === '4'
const isPressureUnit = (value: string | null): value is PressureUnit =>
  value === 'kPa' || value === 'bar' || value === 'psia'
const isPressureProfileId = (value: string | null): value is PressureProfileId =>
  PRESSURE_PROFILES.some((profile) => profile.id === value)

const modules = [
  'Overview',
  'Projects',
  'Streams',
  'Equipment',
  'Calculations',
  'Reports',
  'Settings',
] as const

function App() {
  const [activeTab, setActiveTab] = useState<(typeof modules)[number]>('Overview')
  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [catalogOptions, setCatalogOptions] = useState<PipeCatalogOptions>({
    nominal_sizes: [],
    dn_sizes: [],
    schedules: [],
    materials: [],
  })
  const [pipeCatalog, setPipeCatalog] = useState<PipeRecord[]>([])
  const [selectedPipeId, setSelectedPipeId] = useState<number | null>(null)
  const [selectedNominalSize, setSelectedNominalSize] = useState('')
  const [selectedDnSize, setSelectedDnSize] = useState('')
  const [selectedSchedule, setSelectedSchedule] = useState('')
  const [selectedMaterial, setSelectedMaterial] = useState('')
  const [displayUnit, setDisplayUnit] = useState<DisplayUnit>('mm')
  const [decimalPlaces, setDecimalPlaces] = useState<DecimalPlaces>(3)
  const [pressureUnit, setPressureUnit] = useState<PressureUnit>('kPa')
  const [pressureProfileId, setPressureProfileId] = useState<PressureProfileId>('sea-level')
  const [atmosphericPressureKpa, setAtmosphericPressureKpa] = useState<number>(STANDARD_SEA_LEVEL_PRESSURE_KPA)
  const [atmosphericPressureInput, setAtmosphericPressureInput] = useState<string>(STANDARD_SEA_LEVEL_PRESSURE_KPA.toFixed(3))
  const [hasInitializedPreferences, setHasInitializedPreferences] = useState(false)
  const [catalogRefreshKey, setCatalogRefreshKey] = useState(0)
  const [isHealthLoading, setIsHealthLoading] = useState(true)
  const [isCatalogLoading, setIsCatalogLoading] = useState(true)
  const [healthError, setHealthError] = useState<string | null>(null)
  const [catalogError, setCatalogError] = useState<string | null>(null)
  const [settingsSyncError, setSettingsSyncError] = useState<string | null>(null)
  const [hydraulicsModel, setHydraulicsModel] = useState<HydraulicsModel>('liquid')
  const [isHydraulicsLoading, setIsHydraulicsLoading] = useState(false)
  const [hydraulicsError, setHydraulicsError] = useState<string | null>(null)
  const [hydraulicsResult, setHydraulicsResult] = useState<Record<string, unknown> | null>(null)
  const [hydraulicsWarnings, setHydraulicsWarnings] = useState<string[]>([])
  const [liquidInputs, setLiquidInputs] = useState({
    volumetric_flow_m3_s: '0.01',
    inside_diameter_m: '0.0525',
    pipe_length_m: '120',
    fluid_density_kg_m3: '998',
    dynamic_viscosity_pa_s: '0.001',
    absolute_roughness_m: '0.000045',
    elevation_change_m: '0',
    inlet_pressure_pa: '300000',
  })
  const [gasLowDpInputs, setGasLowDpInputs] = useState({
    mass_flow_kg_s: '0.8',
    inside_diameter_m: '0.1',
    pipe_length_m: '100',
    inlet_pressure_pa: '500000',
    gas_temperature_k: '300',
    molecular_weight_kg_kmol: '18',
    compressibility_factor: '0.98',
    heat_capacity_ratio: '1.33',
    dynamic_viscosity_pa_s: '0.000012',
    absolute_roughness_m: '0.000045',
  })
  const [gasHighDpInputs, setGasHighDpInputs] = useState({
    mass_flow_kg_s: '1.2',
    inside_diameter_m: '0.08',
    pipe_length_m: '150',
    upstream_pressure_pa: '900000',
    downstream_pressure_pa: '350000',
    gas_temperature_k: '310',
    molecular_weight_kg_kmol: '20',
    compressibility_factor: '0.95',
    heat_capacity_ratio: '1.31',
    dynamic_viscosity_pa_s: '0.000015',
    absolute_roughness_m: '0.000045',
  })

  useEffect(() => {
    const controller = new AbortController()

    const loadHealth = async () => {
      try {
        setIsHealthLoading(true)
        const response = await fetch('/api/v1/health', { signal: controller.signal })

        if (!response.ok) {
          throw new Error(`Backend health check failed with ${response.status}`)
        }

        const payload = (await response.json()) as HealthResponse
        setHealth(payload)
        setHealthError(null)
      } catch (loadError) {
        if (loadError instanceof Error && loadError.name !== 'AbortError') {
          setHealthError(loadError.message)
        }
      } finally {
        if (!controller.signal.aborted) {
          setIsHealthLoading(false)
        }
      }
    }

    const loadCatalogOptions = async () => {
      try {
        const preferencesResponse = await fetch('/api/v1/settings/preferences', { signal: controller.signal })
        let backendPreferences: {
          length_unit?: DisplayUnit
          decimal_precision?: DecimalPlaces
          pressure_unit?: PressureUnit
          pressure_profile?: PressureProfileId
          atmospheric_pressure_kpa?: number
        } = {}
        if (preferencesResponse.ok) {
          const preferencesPayload = (await preferencesResponse.json()) as Record<string, unknown>
          backendPreferences = {
            length_unit: isDisplayUnit(String(preferencesPayload.length_unit ?? '')) ? (preferencesPayload.length_unit as DisplayUnit) : undefined,
            decimal_precision: isDecimalPlaces(String(preferencesPayload.decimal_precision ?? ''))
              ? (Number(preferencesPayload.decimal_precision) as DecimalPlaces)
              : undefined,
            pressure_unit: isPressureUnit(String(preferencesPayload.pressure_unit ?? ''))
              ? (preferencesPayload.pressure_unit as PressureUnit)
              : undefined,
            pressure_profile: isPressureProfileId(String(preferencesPayload.pressure_profile ?? ''))
              ? (preferencesPayload.pressure_profile as PressureProfileId)
              : undefined,
            atmospheric_pressure_kpa:
              typeof preferencesPayload.atmospheric_pressure_kpa === 'number'
                ? preferencesPayload.atmospheric_pressure_kpa
                : undefined,
          }
        }

        const response = await fetch('/api/v1/pipe-catalog/options', { signal: controller.signal })
        if (!response.ok) {
          throw new Error(`Pipe catalog options request failed with ${response.status}`)
        }

        const payload = (await response.json()) as Partial<PipeCatalogOptions>
        const normalizedOptions: PipeCatalogOptions = {
          nominal_sizes: Array.isArray(payload.nominal_sizes) ? payload.nominal_sizes : [],
          dn_sizes: Array.isArray(payload.dn_sizes) ? payload.dn_sizes : [],
          schedules: Array.isArray(payload.schedules) ? payload.schedules : [],
          materials: Array.isArray(payload.materials) ? payload.materials : [],
        }

        setCatalogOptions(normalizedOptions)
        const searchParams = new URLSearchParams(window.location.search)
        const urlNominal = searchParams.get('nominal_size')
        const urlDn = searchParams.get('dn_size')
        const urlSchedule = searchParams.get('schedule')
        const urlMaterial = searchParams.get('material')
        const urlUnit = searchParams.get('unit')
        const urlPrecision = searchParams.get('precision')
        const urlPressureUnit = searchParams.get('p_unit')
        const urlPressureProfile = searchParams.get('p_profile')
        const urlPressure = searchParams.get('p_atm')
        const storedUnit = window.localStorage.getItem(DISPLAY_UNIT_STORAGE_KEY)
        const storedPrecision = window.localStorage.getItem(DISPLAY_PRECISION_STORAGE_KEY)
        const storedPressureUnit = window.localStorage.getItem(PRESSURE_UNIT_STORAGE_KEY)
        const storedPressureProfile = window.localStorage.getItem(PRESSURE_PROFILE_STORAGE_KEY)
        const storedPressure = window.localStorage.getItem(ATM_PRESSURE_STORAGE_KEY)

        const initialNominal =
          urlNominal && normalizedOptions.nominal_sizes.includes(urlNominal) ? urlNominal : ALL_FILTER_OPTION
        const initialDn = urlDn && normalizedOptions.dn_sizes.includes(urlDn) ? urlDn : ALL_FILTER_OPTION
        const initialSchedule =
          urlSchedule && normalizedOptions.schedules.includes(urlSchedule) ? urlSchedule : ALL_FILTER_OPTION
        const initialMaterial =
          urlMaterial && normalizedOptions.materials.includes(urlMaterial) ? urlMaterial : ALL_FILTER_OPTION
        const initialUnit = isDisplayUnit(urlUnit)
          ? urlUnit
          : backendPreferences.length_unit
            ? backendPreferences.length_unit
            : isDisplayUnit(storedUnit)
              ? storedUnit
              : 'mm'
        const initialPrecision = isDecimalPlaces(urlPrecision)
          ? Number(urlPrecision)
          : backendPreferences.decimal_precision
            ? backendPreferences.decimal_precision
          : isDecimalPlaces(storedPrecision)
            ? Number(storedPrecision)
            : 3
        const parsedUrlPressure = urlPressure === null ? Number.NaN : Number(urlPressure)
        const parsedStoredPressure = storedPressure === null ? Number.NaN : Number(storedPressure)
        const initialPressureUnit = isPressureUnit(urlPressureUnit)
          ? urlPressureUnit
          : backendPreferences.pressure_unit
            ? backendPreferences.pressure_unit
          : isPressureUnit(storedPressureUnit)
            ? storedPressureUnit
            : 'kPa'
        const rawInitialPressureProfile = isPressureProfileId(urlPressureProfile)
          ? urlPressureProfile
          : backendPreferences.pressure_profile
            ? backendPreferences.pressure_profile
            : isPressureProfileId(storedPressureProfile)
              ? storedPressureProfile
              : 'sea-level'
        const initialAtmosphericPressureKpa = Number.isFinite(parsedUrlPressure) && parsedUrlPressure > 0
          ? parsedUrlPressure
          : typeof backendPreferences.atmospheric_pressure_kpa === 'number' && backendPreferences.atmospheric_pressure_kpa > 0
            ? backendPreferences.atmospheric_pressure_kpa
          : Number.isFinite(parsedStoredPressure) && parsedStoredPressure > 0
            ? parsedStoredPressure
            : STANDARD_SEA_LEVEL_PRESSURE_KPA
        const matchedProfile = PRESSURE_PROFILES.find(
          (profile) => Math.abs(profile.pressureKpa - initialAtmosphericPressureKpa) < 0.05
        )
        const initialPressureProfile =
          rawInitialPressureProfile === 'custom' || !matchedProfile
            ? (backendPreferences.pressure_profile ?? rawInitialPressureProfile)
            : matchedProfile.id

        setSelectedNominalSize((current) => current || initialNominal)
        setSelectedDnSize((current) => current || initialDn)
        setSelectedSchedule((current) => current || initialSchedule)
        setSelectedMaterial((current) => current || initialMaterial)
        setDisplayUnit(initialUnit)
        setDecimalPlaces(initialPrecision as DecimalPlaces)
        setPressureUnit(initialPressureUnit)
        setPressureProfileId(initialPressureProfile)
        setAtmosphericPressureKpa(initialAtmosphericPressureKpa)
        setAtmosphericPressureInput(initialAtmosphericPressureKpa.toFixed(3))
        setCatalogError(null)
        setHasInitializedPreferences(true)
      } catch (loadError) {
        if (loadError instanceof Error && loadError.name !== 'AbortError') {
          setCatalogError(loadError.message)
        }
      }
    }

    void loadHealth()
    void loadCatalogOptions()

    return () => controller.abort()
  }, [])

  useEffect(() => {
    if (!selectedNominalSize || !selectedDnSize || !selectedSchedule || !selectedMaterial) {
      return
    }

    const controller = new AbortController()

    const loadPipes = async (): Promise<void> => {
      const fetchCatalog = async (): Promise<PipeRecord[]> => {
        const params = new URLSearchParams()
        if (selectedNominalSize !== ALL_FILTER_OPTION) {
          params.set('nominal_size', selectedNominalSize)
        }
        if (selectedDnSize !== ALL_FILTER_OPTION) {
          params.set('dn_size', selectedDnSize)
        }
        if (selectedSchedule !== ALL_FILTER_OPTION) {
          params.set('schedule', selectedSchedule)
        }
        if (selectedMaterial !== ALL_FILTER_OPTION) {
          params.set('material', selectedMaterial)
        }

        const query = params.toString()
        const response = await fetch(`/api/v1/pipe-catalog${query ? `?${query}` : ''}`, { signal: controller.signal })
        if (!response.ok) {
          throw new Error(`Pipe catalog request failed with ${response.status}`)
        }

        return (await response.json()) as PipeRecord[]
      }

      try {
        setIsCatalogLoading(true)
        setCatalogError(null)
        let payload: PipeRecord[]
        try {
          payload = await fetchCatalog()
        } catch (firstError) {
          const isTransientNetworkError =
            firstError instanceof TypeError ||
            (firstError instanceof Error && firstError.message.toLowerCase().includes('failed to fetch'))

          if (!isTransientNetworkError || controller.signal.aborted) {
            throw firstError
          }

          await new Promise((resolve) => setTimeout(resolve, 1000))
          if (controller.signal.aborted) {
            return
          }
          payload = await fetchCatalog()
        }

        setPipeCatalog(payload)
        setSelectedPipeId((current) => {
          if (current !== null && payload.some((pipe) => pipe.id === current)) {
            return current
          }
          return payload[0]?.id ?? null
        })
        setCatalogError(null)
      } catch (loadError) {
        if (loadError instanceof Error && loadError.name !== 'AbortError') {
          setPipeCatalog([])
          setSelectedPipeId(null)
          setCatalogError(`Unable to refresh pipe catalog: ${loadError.message}`)
        }
      } finally {
        if (!controller.signal.aborted) {
          setIsCatalogLoading(false)
        }
      }
    }

    void loadPipes()

    return () => controller.abort()
  }, [selectedNominalSize, selectedDnSize, selectedSchedule, selectedMaterial, catalogRefreshKey])

  useEffect(() => {
    if (!selectedNominalSize || !selectedDnSize || !selectedSchedule || !selectedMaterial) {
      return
    }

    const params = new URLSearchParams()
    if (selectedNominalSize !== ALL_FILTER_OPTION) {
      params.set('nominal_size', selectedNominalSize)
    }
    if (selectedDnSize !== ALL_FILTER_OPTION) {
      params.set('dn_size', selectedDnSize)
    }
    if (selectedSchedule !== ALL_FILTER_OPTION) {
      params.set('schedule', selectedSchedule)
    }
    if (selectedMaterial !== ALL_FILTER_OPTION) {
      params.set('material', selectedMaterial)
    }
    if (displayUnit !== 'mm') {
      params.set('unit', displayUnit)
    }
    if (decimalPlaces !== 3) {
      params.set('precision', String(decimalPlaces))
    }
    if (pressureUnit !== 'kPa') {
      params.set('p_unit', pressureUnit)
    }
    if (pressureProfileId !== 'sea-level') {
      params.set('p_profile', pressureProfileId)
    }
    if (Math.abs(atmosphericPressureKpa - STANDARD_SEA_LEVEL_PRESSURE_KPA) > 1e-9) {
      params.set('p_atm', atmosphericPressureKpa.toFixed(3))
    }

    const query = params.toString()
    const nextUrl = `${window.location.pathname}${query ? `?${query}` : ''}`
    window.history.replaceState(null, '', nextUrl)
  }, [
    selectedNominalSize,
    selectedDnSize,
    selectedSchedule,
    selectedMaterial,
    displayUnit,
    decimalPlaces,
    pressureUnit,
    pressureProfileId,
    atmosphericPressureKpa,
  ])

  useEffect(() => {
    window.localStorage.setItem(DISPLAY_UNIT_STORAGE_KEY, displayUnit)
  }, [displayUnit])

  useEffect(() => {
    window.localStorage.setItem(DISPLAY_PRECISION_STORAGE_KEY, String(decimalPlaces))
  }, [decimalPlaces])

  useEffect(() => {
    window.localStorage.setItem(PRESSURE_UNIT_STORAGE_KEY, pressureUnit)
  }, [pressureUnit])

  useEffect(() => {
    window.localStorage.setItem(PRESSURE_PROFILE_STORAGE_KEY, pressureProfileId)
  }, [pressureProfileId])

  useEffect(() => {
    window.localStorage.setItem(ATM_PRESSURE_STORAGE_KEY, atmosphericPressureKpa.toFixed(6))
  }, [atmosphericPressureKpa])

  useEffect(() => {
    if (!hasInitializedPreferences) {
      return
    }

    const savePreferences = async () => {
      try {
        const response = await fetch('/api/v1/settings/preferences', {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            length_unit: displayUnit,
            decimal_precision: decimalPlaces,
            pressure_unit: pressureUnit,
            pressure_profile: pressureProfileId,
            atmospheric_pressure_kpa: atmosphericPressureKpa,
          }),
        })
        if (!response.ok) {
          throw new Error(`Settings update failed with ${response.status}`)
        }
        setSettingsSyncError(null)
      } catch (saveError) {
        if (saveError instanceof Error) {
          setSettingsSyncError(saveError.message)
        }
      }
    }

    void savePreferences()
  }, [hasInitializedPreferences, displayUnit, decimalPlaces, pressureUnit, pressureProfileId, atmosphericPressureKpa])

  const backendStatus = health ? (health.status === 'ok' ? 'Healthy' : 'Degraded') : 'Checking...'
  const selectedRecord = pipeCatalog.find((pipe) => pipe.id === selectedPipeId) ?? pipeCatalog[0] ?? null
  const nominalSizeOptions = [ALL_FILTER_OPTION, ...catalogOptions.nominal_sizes]
  const dnSizeOptions = [ALL_FILTER_OPTION, ...catalogOptions.dn_sizes]
  const scheduleOptions = [ALL_FILTER_OPTION, ...catalogOptions.schedules]
  const materialOptions = [ALL_FILTER_OPTION, ...catalogOptions.materials]
  const lengthUnitLabel = displayUnit === 'mm' ? 'mm' : 'in'
  const pressureUnitLabel = pressureUnit
  const formatLength = (inches: number) => (displayUnit === 'mm' ? inches * INCH_TO_MM : inches).toFixed(decimalPlaces)
  const formatRoughness = (millimeters: number) =>
    (displayUnit === 'mm' ? millimeters : millimeters / INCH_TO_MM).toFixed(decimalPlaces)
  const formatPressure = (kpa: number) => {
    if (pressureUnit === 'kPa') {
      return kpa.toFixed(3)
    }
    if (pressureUnit === 'bar') {
      return (kpa / 100).toFixed(4)
    }
    return (kpa / 6.894757293168361).toFixed(4)
  }
  const convertFromPressureUnit = (value: number) => {
    if (pressureUnit === 'kPa') {
      return value
    }
    if (pressureUnit === 'bar') {
      return value * 100
    }
    return value * 6.894757293168361
  }
  const resetFilters = () => {
    setSelectedNominalSize(ALL_FILTER_OPTION)
    setSelectedDnSize(ALL_FILTER_OPTION)
    setSelectedSchedule(ALL_FILTER_OPTION)
    setSelectedMaterial(ALL_FILTER_OPTION)
  }
  const retryCatalogFetch = () => {
    setCatalogRefreshKey((current) => current + 1)
  }
  const applyMetricDefaults = () => {
    setDisplayUnit('mm')
    setDecimalPlaces(3)
  }
  const applyImperialDefaults = () => {
    setDisplayUnit('in')
    setDecimalPlaces(4)
  }
  const applySeaLevelAtmosphericPressure = () => {
    setPressureProfileId('sea-level')
    setAtmosphericPressureKpa(STANDARD_SEA_LEVEL_PRESSURE_KPA)
    setAtmosphericPressureInput(formatPressure(STANDARD_SEA_LEVEL_PRESSURE_KPA))
  }
  const atmosphericPressureDisplay = formatPressure(atmosphericPressureKpa)
  const activePressureProfile = PRESSURE_PROFILES.find((profile) => profile.id === pressureProfileId) ?? PRESSURE_PROFILES[0]
  const updateLiquidInput = (field: keyof typeof liquidInputs, value: string) => {
    setLiquidInputs((current) => ({ ...current, [field]: value }))
  }
  const updateGasLowDpInput = (field: keyof typeof gasLowDpInputs, value: string) => {
    setGasLowDpInputs((current) => ({ ...current, [field]: value }))
  }
  const updateGasHighDpInput = (field: keyof typeof gasHighDpInputs, value: string) => {
    setGasHighDpInputs((current) => ({ ...current, [field]: value }))
  }

  const submitHydraulicsCalculation = async () => {
    setIsHydraulicsLoading(true)
    setHydraulicsError(null)
    try {
      let endpoint = '/api/v1/hydraulics/liquid-pipe'
      let payload: Record<string, unknown> = {}

      if (hydraulicsModel === 'liquid') {
        payload = {
          volumetric_flow_m3_s: Number(liquidInputs.volumetric_flow_m3_s),
          inside_diameter_m: Number(liquidInputs.inside_diameter_m),
          pipe_length_m: Number(liquidInputs.pipe_length_m),
          fluid_density_kg_m3: Number(liquidInputs.fluid_density_kg_m3),
          dynamic_viscosity_pa_s: Number(liquidInputs.dynamic_viscosity_pa_s),
          absolute_roughness_m: Number(liquidInputs.absolute_roughness_m),
          elevation_change_m: Number(liquidInputs.elevation_change_m),
          inlet_pressure_pa: Number(liquidInputs.inlet_pressure_pa),
          include_fittings: false,
          fittings_method: 'none',
          fittings_k_total: 0,
        }
      } else if (hydraulicsModel === 'gas-low-dp') {
        endpoint = '/api/v1/hydraulics/gas-pipe/low-dp'
        payload = {
          mass_flow_kg_s: Number(gasLowDpInputs.mass_flow_kg_s),
          inside_diameter_m: Number(gasLowDpInputs.inside_diameter_m),
          pipe_length_m: Number(gasLowDpInputs.pipe_length_m),
          inlet_pressure_pa: Number(gasLowDpInputs.inlet_pressure_pa),
          gas_temperature_k: Number(gasLowDpInputs.gas_temperature_k),
          molecular_weight_kg_kmol: Number(gasLowDpInputs.molecular_weight_kg_kmol),
          compressibility_factor: Number(gasLowDpInputs.compressibility_factor),
          heat_capacity_ratio: Number(gasLowDpInputs.heat_capacity_ratio),
          dynamic_viscosity_pa_s: Number(gasLowDpInputs.dynamic_viscosity_pa_s),
          absolute_roughness_m: Number(gasLowDpInputs.absolute_roughness_m),
          include_fittings: false,
          fittings_method: 'none',
          fittings_k_total: 0,
        }
      } else {
        endpoint = '/api/v1/hydraulics/gas-pipe/high-dp'
        payload = {
          mass_flow_kg_s: Number(gasHighDpInputs.mass_flow_kg_s),
          inside_diameter_m: Number(gasHighDpInputs.inside_diameter_m),
          pipe_length_m: Number(gasHighDpInputs.pipe_length_m),
          upstream_pressure_pa: Number(gasHighDpInputs.upstream_pressure_pa),
          downstream_pressure_pa: Number(gasHighDpInputs.downstream_pressure_pa),
          gas_temperature_k: Number(gasHighDpInputs.gas_temperature_k),
          molecular_weight_kg_kmol: Number(gasHighDpInputs.molecular_weight_kg_kmol),
          compressibility_factor: Number(gasHighDpInputs.compressibility_factor),
          heat_capacity_ratio: Number(gasHighDpInputs.heat_capacity_ratio),
          dynamic_viscosity_pa_s: Number(gasHighDpInputs.dynamic_viscosity_pa_s),
          absolute_roughness_m: Number(gasHighDpInputs.absolute_roughness_m),
          include_fittings: false,
          fittings_method: 'none',
          fittings_k_total: 0,
        }
      }

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
      const responsePayload = (await response.json()) as Record<string, unknown>
      if (!response.ok) {
        const detail = typeof responsePayload.detail === 'string' ? responsePayload.detail : `Request failed with ${response.status}`
        throw new Error(detail)
      }
      setHydraulicsResult(responsePayload)
      setHydraulicsWarnings(Array.isArray(responsePayload.warnings) ? responsePayload.warnings.filter((entry): entry is string => typeof entry === 'string') : [])
    } catch (calculationError) {
      if (calculationError instanceof Error) {
        setHydraulicsError(calculationError.message)
      } else {
        setHydraulicsError('Hydraulics request failed.')
      }
      setHydraulicsResult(null)
      setHydraulicsWarnings([])
    } finally {
      setIsHydraulicsLoading(false)
    }
  }
  const formatHydraulicsValue = (value: unknown) => {
    if (typeof value === 'number') {
      return Number.isFinite(value) ? value.toLocaleString(undefined, { maximumFractionDigits: 6 }) : String(value)
    }
    if (typeof value === 'boolean') {
      return value ? 'Yes' : 'No'
    }
    return String(value)
  }
  const hydraulicsResultEntries = hydraulicsResult
    ? Object.entries(hydraulicsResult).filter(([key, value]) => key !== 'warnings' && typeof value !== 'object')
    : []

  const moduleCopy: Record<(typeof modules)[number], string> = {
    Overview:
      'Application shell, backend connectivity, and the engineering workflow infrastructure are in place for the next process-design modules.',
    Projects:
      'Project workspace placeholders are prepared for future case and design-portfolio management.',
    Streams:
      'Reusable stream definitions and flow metadata are planned here without implementing process calculations.',
    Equipment:
      'Pipe, valve, vessel, and other equipment modules will be added in later phases.',
    Calculations:
      'Hydraulics models are now available for liquid, gas low-ΔP, and gas high-ΔP workflows.',
    Reports:
      'Result-view and reporting layout placeholders are staged for later engineering outputs.',
    Settings:
      'Application configuration, units system, and database metadata can be extended here without affecting Phase 1 scope.',
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand-block">
          <p className="eyebrow">Process Design Suite</p>
          <h2>Phase 2</h2>
        </div>

        <nav className="navigation" aria-label="Main application navigation">
          {modules.map((module) => (
            <Button
              key={module}
              className={`nav-button ${activeTab === module ? 'active' : ''}`}
              variant={activeTab === module ? 'primary' : 'outline'}
              onPress={() => setActiveTab(module)}
            >
              {module}
            </Button>
          ))}
        </nav>
      </aside>

      <main className="main-panel">
        <header className="topbar">
          <div>
            <p className="eyebrow">Engineering platform</p>
            <h1>Pipe Database</h1>
          </div>
          <Chip color={health?.status === 'ok' ? 'success' : 'warning'}>{backendStatus}</Chip>
        </header>

        <Card className="content-card">
          <Card.Header>
            <div>
              <p className="eyebrow">Module</p>
              <h3>{activeTab}</h3>
            </div>
          </Card.Header>
          <div className="card-divider" />
          <Card.Content>
            <p className="module-copy">{moduleCopy[activeTab]}</p>
          </Card.Content>
        </Card>

        {activeTab === 'Settings' ? (
          <Card className="settings-card">
            <Card.Header>
              <h3>Unit preferences</h3>
            </Card.Header>
            <div className="card-divider" />
            <Card.Content>
              <div className="settings-grid">
                <label className="field">
                  <span>Length display unit</span>
                  <select
                    value={displayUnit}
                    onChange={(event) => {
                      const nextUnit = event.target.value
                      if (isDisplayUnit(nextUnit)) {
                        setDisplayUnit(nextUnit)
                      }
                    }}
                  >
                    <option value="mm">Millimeters (mm)</option>
                    <option value="in">Inches (in)</option>
                  </select>
                </label>

                <label className="field">
                  <span>Decimal precision</span>
                  <select
                    value={String(decimalPlaces)}
                    onChange={(event) => {
                      if (isDecimalPlaces(event.target.value)) {
                        setDecimalPlaces(Number(event.target.value) as DecimalPlaces)
                      }
                    }}
                  >
                    <option value="2">2 decimals</option>
                    <option value="3">3 decimals</option>
                    <option value="4">4 decimals</option>
                  </select>
                </label>

                <label className="field">
                  <span>Atmospheric profile / elevation</span>
                  <select
                    value={pressureProfileId}
                    onChange={(event) => {
                      const nextProfile = event.target.value
                      if (!isPressureProfileId(nextProfile)) {
                        return
                      }
                      setPressureProfileId(nextProfile)
                      if (nextProfile !== 'custom') {
                        const profile = PRESSURE_PROFILES.find((item) => item.id === nextProfile)
                        if (profile) {
                          setAtmosphericPressureKpa(profile.pressureKpa)
                          setAtmosphericPressureInput(formatPressure(profile.pressureKpa))
                        }
                      }
                    }}
                  >
                    {PRESSURE_PROFILES.map((profile) => (
                      <option key={profile.id} value={profile.id}>
                        {profile.label}
                      </option>
                    ))}
                  </select>
                </label>

                <label className="field">
                  <span>Atmospheric pressure unit</span>
                  <select
                    value={pressureUnit}
                    onChange={(event) => {
                      const nextUnit = event.target.value
                      if (isPressureUnit(nextUnit)) {
                        setPressureUnit(nextUnit)
                        setAtmosphericPressureInput(
                          nextUnit === 'kPa'
                            ? atmosphericPressureKpa.toFixed(3)
                            : nextUnit === 'bar'
                              ? (atmosphericPressureKpa / 100).toFixed(4)
                              : (atmosphericPressureKpa / 6.894757293168361).toFixed(4)
                        )
                      }
                    }}
                  >
                    <option value="kPa">kPa</option>
                    <option value="bar">bar</option>
                    <option value="psia">psia</option>
                  </select>
                </label>

                <label className="field">
                  <span>{`Atmospheric pressure (${pressureUnitLabel}, absolute)`}</span>
                  <input
                    className="field-input"
                    type="number"
                    min="0"
                    step="0.0001"
                    value={atmosphericPressureInput}
                    onChange={(event) => setAtmosphericPressureInput(event.target.value)}
                    onBlur={() => {
                      const parsed = Number(atmosphericPressureInput)
                      if (!Number.isFinite(parsed) || parsed <= 0) {
                        setAtmosphericPressureInput(formatPressure(atmosphericPressureKpa))
                        return
                      }
                      const converted = convertFromPressureUnit(parsed)
                      setPressureProfileId('custom')
                      setAtmosphericPressureKpa(converted)
                      setAtmosphericPressureInput(formatPressure(converted))
                    }}
                  />
                  <small className="field-help">
                    Use sea-level standard or your local site pressure for elevation-specific process design contexts.
                  </small>
                </label>
              </div>
              <div className="settings-actions">
                <Button variant="outline" onPress={applyMetricDefaults}>
                  Use metric defaults
                </Button>
                <Button variant="outline" onPress={applyImperialDefaults}>
                  Use imperial defaults
                </Button>
                <Button variant="outline" onPress={applySeaLevelAtmosphericPressure}>
                  Use sea-level atmosphere
                </Button>
              </div>
              <p className="settings-summary">{`Current atmospheric pressure: ${atmosphericPressureDisplay} ${pressureUnitLabel} (abs)`}</p>
              <p className="settings-summary-secondary">
                {activePressureProfile.elevationM === null
                  ? 'Active profile: Custom local pressure'
                  : `Active profile elevation reference: ${activePressureProfile.elevationM} m above sea level`}
              </p>
              {settingsSyncError ? <p className="settings-sync-error">{`Settings sync warning: ${settingsSyncError}`}</p> : null}
            </Card.Content>
          </Card>
        ) : null}

        {activeTab === 'Calculations' ? (
          <Card className="hydraulics-card">
            <Card.Header>
              <h3>Hydraulics workspace</h3>
            </Card.Header>
            <div className="card-divider" />
            <Card.Content>
              <div className="settings-grid">
                <label className="field">
                  <span>Calculation model</span>
                  <select value={hydraulicsModel} onChange={(event) => setHydraulicsModel(event.target.value as HydraulicsModel)}>
                    <option value="liquid">Liquid pipe (incompressible)</option>
                    <option value="gas-low-dp">Gas pipe (low-ΔP)</option>
                    <option value="gas-high-dp">Gas pipe (high-ΔP / high-Mach)</option>
                  </select>
                </label>
              </div>

              {hydraulicsModel === 'liquid' ? (
                <div className="hydraulics-grid">
                  <label className="field">
                    <span>Flow rate (m³/s)</span>
                    <input className="field-input" type="number" step="0.0001" value={liquidInputs.volumetric_flow_m3_s} onChange={(event) => updateLiquidInput('volumetric_flow_m3_s', event.target.value)} />
                  </label>
                  <label className="field">
                    <span>Inside diameter (m)</span>
                    <input className="field-input" type="number" step="0.0001" value={liquidInputs.inside_diameter_m} onChange={(event) => updateLiquidInput('inside_diameter_m', event.target.value)} />
                  </label>
                  <label className="field">
                    <span>Pipe length (m)</span>
                    <input className="field-input" type="number" step="0.1" value={liquidInputs.pipe_length_m} onChange={(event) => updateLiquidInput('pipe_length_m', event.target.value)} />
                  </label>
                  <label className="field">
                    <span>Density (kg/m³)</span>
                    <input className="field-input" type="number" step="0.1" value={liquidInputs.fluid_density_kg_m3} onChange={(event) => updateLiquidInput('fluid_density_kg_m3', event.target.value)} />
                  </label>
                  <label className="field">
                    <span>Viscosity (Pa·s)</span>
                    <input className="field-input" type="number" step="0.000001" value={liquidInputs.dynamic_viscosity_pa_s} onChange={(event) => updateLiquidInput('dynamic_viscosity_pa_s', event.target.value)} />
                  </label>
                  <label className="field">
                    <span>Absolute roughness (m)</span>
                    <input className="field-input" type="number" step="0.000001" value={liquidInputs.absolute_roughness_m} onChange={(event) => updateLiquidInput('absolute_roughness_m', event.target.value)} />
                  </label>
                  <label className="field">
                    <span>Elevation change (m)</span>
                    <input className="field-input" type="number" step="0.1" value={liquidInputs.elevation_change_m} onChange={(event) => updateLiquidInput('elevation_change_m', event.target.value)} />
                  </label>
                  <label className="field">
                    <span>Inlet pressure (Pa abs)</span>
                    <input className="field-input" type="number" step="1" value={liquidInputs.inlet_pressure_pa} onChange={(event) => updateLiquidInput('inlet_pressure_pa', event.target.value)} />
                  </label>
                </div>
              ) : null}

              {hydraulicsModel === 'gas-low-dp' ? (
                <div className="hydraulics-grid">
                  <label className="field">
                    <span>Mass flow (kg/s)</span>
                    <input className="field-input" type="number" step="0.001" value={gasLowDpInputs.mass_flow_kg_s} onChange={(event) => updateGasLowDpInput('mass_flow_kg_s', event.target.value)} />
                  </label>
                  <label className="field">
                    <span>Inside diameter (m)</span>
                    <input className="field-input" type="number" step="0.0001" value={gasLowDpInputs.inside_diameter_m} onChange={(event) => updateGasLowDpInput('inside_diameter_m', event.target.value)} />
                  </label>
                  <label className="field">
                    <span>Pipe length (m)</span>
                    <input className="field-input" type="number" step="0.1" value={gasLowDpInputs.pipe_length_m} onChange={(event) => updateGasLowDpInput('pipe_length_m', event.target.value)} />
                  </label>
                  <label className="field">
                    <span>Inlet pressure (Pa abs)</span>
                    <input className="field-input" type="number" step="1" value={gasLowDpInputs.inlet_pressure_pa} onChange={(event) => updateGasLowDpInput('inlet_pressure_pa', event.target.value)} />
                  </label>
                  <label className="field">
                    <span>Temperature (K)</span>
                    <input className="field-input" type="number" step="0.1" value={gasLowDpInputs.gas_temperature_k} onChange={(event) => updateGasLowDpInput('gas_temperature_k', event.target.value)} />
                  </label>
                  <label className="field">
                    <span>Molecular weight (kg/kmol)</span>
                    <input className="field-input" type="number" step="0.01" value={gasLowDpInputs.molecular_weight_kg_kmol} onChange={(event) => updateGasLowDpInput('molecular_weight_kg_kmol', event.target.value)} />
                  </label>
                  <label className="field">
                    <span>Compressibility factor (Z)</span>
                    <input className="field-input" type="number" step="0.001" value={gasLowDpInputs.compressibility_factor} onChange={(event) => updateGasLowDpInput('compressibility_factor', event.target.value)} />
                  </label>
                  <label className="field">
                    <span>Heat capacity ratio (γ)</span>
                    <input className="field-input" type="number" step="0.01" value={gasLowDpInputs.heat_capacity_ratio} onChange={(event) => updateGasLowDpInput('heat_capacity_ratio', event.target.value)} />
                  </label>
                  <label className="field">
                    <span>Viscosity (Pa·s)</span>
                    <input className="field-input" type="number" step="0.000001" value={gasLowDpInputs.dynamic_viscosity_pa_s} onChange={(event) => updateGasLowDpInput('dynamic_viscosity_pa_s', event.target.value)} />
                  </label>
                  <label className="field">
                    <span>Absolute roughness (m)</span>
                    <input className="field-input" type="number" step="0.000001" value={gasLowDpInputs.absolute_roughness_m} onChange={(event) => updateGasLowDpInput('absolute_roughness_m', event.target.value)} />
                  </label>
                </div>
              ) : null}

              {hydraulicsModel === 'gas-high-dp' ? (
                <div className="hydraulics-grid">
                  <label className="field">
                    <span>Mass flow (kg/s)</span>
                    <input className="field-input" type="number" step="0.001" value={gasHighDpInputs.mass_flow_kg_s} onChange={(event) => updateGasHighDpInput('mass_flow_kg_s', event.target.value)} />
                  </label>
                  <label className="field">
                    <span>Inside diameter (m)</span>
                    <input className="field-input" type="number" step="0.0001" value={gasHighDpInputs.inside_diameter_m} onChange={(event) => updateGasHighDpInput('inside_diameter_m', event.target.value)} />
                  </label>
                  <label className="field">
                    <span>Pipe length (m)</span>
                    <input className="field-input" type="number" step="0.1" value={gasHighDpInputs.pipe_length_m} onChange={(event) => updateGasHighDpInput('pipe_length_m', event.target.value)} />
                  </label>
                  <label className="field">
                    <span>Upstream pressure (Pa abs)</span>
                    <input className="field-input" type="number" step="1" value={gasHighDpInputs.upstream_pressure_pa} onChange={(event) => updateGasHighDpInput('upstream_pressure_pa', event.target.value)} />
                  </label>
                  <label className="field">
                    <span>Downstream pressure (Pa abs)</span>
                    <input className="field-input" type="number" step="1" value={gasHighDpInputs.downstream_pressure_pa} onChange={(event) => updateGasHighDpInput('downstream_pressure_pa', event.target.value)} />
                  </label>
                  <label className="field">
                    <span>Temperature (K)</span>
                    <input className="field-input" type="number" step="0.1" value={gasHighDpInputs.gas_temperature_k} onChange={(event) => updateGasHighDpInput('gas_temperature_k', event.target.value)} />
                  </label>
                  <label className="field">
                    <span>Molecular weight (kg/kmol)</span>
                    <input className="field-input" type="number" step="0.01" value={gasHighDpInputs.molecular_weight_kg_kmol} onChange={(event) => updateGasHighDpInput('molecular_weight_kg_kmol', event.target.value)} />
                  </label>
                  <label className="field">
                    <span>Compressibility factor (Z)</span>
                    <input className="field-input" type="number" step="0.001" value={gasHighDpInputs.compressibility_factor} onChange={(event) => updateGasHighDpInput('compressibility_factor', event.target.value)} />
                  </label>
                  <label className="field">
                    <span>Heat capacity ratio (γ)</span>
                    <input className="field-input" type="number" step="0.01" value={gasHighDpInputs.heat_capacity_ratio} onChange={(event) => updateGasHighDpInput('heat_capacity_ratio', event.target.value)} />
                  </label>
                  <label className="field">
                    <span>Viscosity (Pa·s)</span>
                    <input className="field-input" type="number" step="0.000001" value={gasHighDpInputs.dynamic_viscosity_pa_s} onChange={(event) => updateGasHighDpInput('dynamic_viscosity_pa_s', event.target.value)} />
                  </label>
                  <label className="field">
                    <span>Absolute roughness (m)</span>
                    <input className="field-input" type="number" step="0.000001" value={gasHighDpInputs.absolute_roughness_m} onChange={(event) => updateGasHighDpInput('absolute_roughness_m', event.target.value)} />
                  </label>
                </div>
              ) : null}

              <div className="hydraulics-actions">
                <Button variant="primary" onPress={submitHydraulicsCalculation} isDisabled={isHydraulicsLoading}>
                  {isHydraulicsLoading ? 'Running...' : 'Run calculation'}
                </Button>
              </div>

              {hydraulicsError ? <p className="error-text">{hydraulicsError}</p> : null}

              {hydraulicsWarnings.length > 0 ? (
                <div className="hydraulics-warnings">
                  <h4>Warnings</h4>
                  <ul>
                    {hydraulicsWarnings.map((warning) => (
                      <li key={warning}>{warning}</li>
                    ))}
                  </ul>
                </div>
              ) : null}

              {hydraulicsResultEntries.length > 0 ? (
                <div className="hydraulics-result-grid">
                  {hydraulicsResultEntries.map(([key, value]) => (
                    <div key={key} className="hydraulics-result-item">
                      <span>{key}</span>
                      <strong>{formatHydraulicsValue(value)}</strong>
                    </div>
                  ))}
                </div>
              ) : null}
            </Card.Content>
          </Card>
        ) : null}

        <section className="details-grid">
          <Card className="status-card">
            <Card.Header>
              <h3>Backend status</h3>
            </Card.Header>
            <div className="card-divider" />
            <Card.Content>
              {healthError ? (
                <p className="error-text">{healthError}</p>
              ) : health ? (
                <div className="status-list">
                  <div>
                    <span>Service</span>
                    <strong>{health.service}</strong>
                  </div>
                  <div>
                    <span>Version</span>
                    <strong>{health.version}</strong>
                  </div>
                  <div>
                    <span>Environment</span>
                    <strong>{health.environment}</strong>
                  </div>
                  <div>
                    <span>Readiness</span>
                    <strong>{health.readiness}</strong>
                  </div>
                  <div>
                    <span>Database</span>
                    <strong>{health.database.status}</strong>
                  </div>
                </div>
              ) : (
                <p>{isHealthLoading ? 'Checking backend health endpoint...' : 'Backend status unavailable.'}</p>
              )}
            </Card.Content>
          </Card>

          <Card className="status-card">
            <Card.Header>
              <h3>Phase 2 scope</h3>
            </Card.Header>
            <div className="card-divider" />
            <Card.Content>
              <ul className="scope-list">
                <li>Pipe dimension catalog</li>
                <li>NPS, DN, and schedule selection</li>
                <li>SQLite-backed repository</li>
                <li>Typed pipe schema</li>
                <li>API catalog endpoint</li>
                <li>Frontend reference selector</li>
              </ul>
            </Card.Content>
          </Card>
        </section>

        <Card className="catalog-card">
          <Card.Header>
            <div className="catalog-header">
              <h3>Pipe selector</h3>
              <div className="catalog-meta">
                <span>{isCatalogLoading ? 'Loading...' : `${pipeCatalog.length} result${pipeCatalog.length === 1 ? '' : 's'}`}</span>
                <span>Reference catalog</span>
              </div>
            </div>
          </Card.Header>
          <div className="card-divider" />
          <Card.Content>
            <div className="selector-row">
              <label className="field">
                <span>Nominal size</span>
                <select value={selectedNominalSize} onChange={(event) => setSelectedNominalSize(event.target.value)}>
                  {nominalSizeOptions.map((size) => (
                    <option key={size} value={size}>
                      {size}
                    </option>
                  ))}
                </select>
              </label>

              <label className="field">
                <span>DN size</span>
                <select value={selectedDnSize} onChange={(event) => setSelectedDnSize(event.target.value)}>
                  {dnSizeOptions.map((size) => (
                    <option key={size} value={size}>
                      {size}
                    </option>
                  ))}
                </select>
              </label>

              <label className="field">
                <span>Schedule</span>
                <select value={selectedSchedule} onChange={(event) => setSelectedSchedule(event.target.value)}>
                  {scheduleOptions.map((schedule) => (
                    <option key={schedule} value={schedule}>
                      {schedule}
                    </option>
                  ))}
                </select>
              </label>

              <label className="field">
                <span>Material</span>
                <select value={selectedMaterial} onChange={(event) => setSelectedMaterial(event.target.value)}>
                  {materialOptions.map((material) => (
                    <option key={material} value={material}>
                      {material}
                    </option>
                  ))}
                </select>
              </label>

              <label className="field">
                <span>Units</span>
                <select
                  value={displayUnit}
                  onChange={(event) => {
                    const nextUnit = event.target.value
                    if (isDisplayUnit(nextUnit)) {
                      setDisplayUnit(nextUnit)
                    }
                  }}
                >
                  <option value="mm">Millimeters (mm)</option>
                  <option value="in">Inches (in)</option>
                </select>
              </label>

              <div className="field action-field">
                <span>Actions</span>
                <Button className="reset-button" variant="outline" onPress={resetFilters}>
                  Reset filters
                </Button>
              </div>
            </div>
            <p className="catalog-hint">Tip: use ↑/↓ to move through rows, then Enter or Space to select one.</p>

            {catalogError ? (
              <div className="error-banner">
                <p className="error-text">{catalogError}</p>
                <Button className="retry-button" variant="outline" onPress={retryCatalogFetch}>
                  Retry
                </Button>
              </div>
            ) : null}

            <div className="key-metrics">
              <div>
                <span>Outside diameter</span>
                <strong>{selectedRecord ? `${formatLength(selectedRecord.outside_diameter_in)} ${lengthUnitLabel}` : '—'}</strong>
              </div>
              <div>
                <span>Wall thickness</span>
                <strong>{selectedRecord ? `${formatLength(selectedRecord.wall_thickness_in)} ${lengthUnitLabel}` : '—'}</strong>
              </div>
              <div>
                <span>Inside diameter</span>
                <strong>{selectedRecord ? `${formatLength(selectedRecord.inside_diameter_in)} ${lengthUnitLabel}` : '—'}</strong>
              </div>
              <div>
                <span>Roughness</span>
                <strong>{selectedRecord && selectedRecord.roughness_mm !== null ? `${formatRoughness(selectedRecord.roughness_mm)} ${lengthUnitLabel}` : '—'}</strong>
              </div>
            </div>

            <div className="table-wrap" role="region" aria-label="Pipe catalog table">
              <table className="pipe-table">
                <thead>
                  <tr>
                    <th>Nominal</th>
                    <th>DN</th>
                    <th>Schedule</th>
                    <th>Material</th>
                    <th>{`OD (${lengthUnitLabel})`}</th>
                    <th>{`Wall (${lengthUnitLabel})`}</th>
                    <th>{`ID (${lengthUnitLabel})`}</th>
                    <th>{`Roughness (${lengthUnitLabel})`}</th>
                  </tr>
                </thead>
                <tbody>
                  {isCatalogLoading ? (
                    <tr>
                      <td colSpan={8}>Loading pipe records...</td>
                    </tr>
                  ) : pipeCatalog.length > 0 ? (
                    pipeCatalog.map((pipe) => (
                      <tr
                        key={pipe.id}
                        data-pipe-id={pipe.id}
                        className={pipe.id === selectedRecord?.id ? 'is-selected' : ''}
                        onClick={() => setSelectedPipeId(pipe.id)}
                        onKeyDown={(event) => {
                          if (event.key === 'Enter' || event.key === ' ') {
                            event.preventDefault()
                            setSelectedPipeId(pipe.id)
                          }
                          if (event.key === 'ArrowDown') {
                            event.preventDefault()
                            const nextRow = event.currentTarget.nextElementSibling as HTMLTableRowElement | null
                            if (nextRow) {
                              nextRow.focus()
                              const nextId = nextRow.dataset.pipeId
                              if (nextId) {
                                setSelectedPipeId(Number(nextId))
                              }
                            }
                          }
                          if (event.key === 'ArrowUp') {
                            event.preventDefault()
                            const previousRow = event.currentTarget.previousElementSibling as HTMLTableRowElement | null
                            if (previousRow) {
                              previousRow.focus()
                              const previousId = previousRow.dataset.pipeId
                              if (previousId) {
                                setSelectedPipeId(Number(previousId))
                              }
                            }
                          }
                        }}
                        tabIndex={0}
                        aria-selected={pipe.id === selectedRecord?.id}
                        aria-label={`Select ${pipe.nominal_size} (${pipe.dn_size}) schedule ${pipe.schedule} ${pipe.material}`}
                      >
                        <td>{pipe.nominal_size}</td>
                        <td>{pipe.dn_size}</td>
                        <td>{pipe.schedule}</td>
                        <td>{pipe.material}</td>
                        <td>{formatLength(pipe.outside_diameter_in)}</td>
                        <td>{formatLength(pipe.wall_thickness_in)}</td>
                        <td>{formatLength(pipe.inside_diameter_in)}</td>
                        <td>{pipe.roughness_mm !== null ? formatRoughness(pipe.roughness_mm) : '—'}</td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={8}>No pipe records match the selected filters.</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </Card.Content>
        </Card>
      </main>
    </div>
  )
}

export default App
