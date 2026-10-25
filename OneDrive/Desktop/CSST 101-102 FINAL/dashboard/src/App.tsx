import { useEffect, useMemo, useState, type ReactNode } from "react"
import dashboardJson from "./data/dashboard.json"
import syntheticDemo from "./data/syntheticDemo.json"

type PageId = "overview" | "water" | "evidence" | "model" | "sources"

type YearPoint = {
  year: number
  n: number
  mean: number | null
  min: number | null
  max: number | null
}

type RainfallYear = {
  year: number
  total: number
  months: number
}

type MonthlyRainfall = {
  month: number
  label: string
  mean: number
  min: number
  max: number
  years: number
}

type WaterVariable = {
  key: string
  label: string
  unit: string
  years: YearPoint[]
  latest: YearPoint | null
  summary: {
    n: number
    mean: number | null
    median: number | null
    min: number | null
    max: number | null
  }
}

type Metric = {
  id: string
  label: string
  value: number | null
  display: string
  unit: string
  period: string
  detail: string
  note: string
  points: Array<number | null>
}

type Measurement = {
  station: string
  zone: string
  year: number
  variable: string
  value: number
  unit: string
  quality: string
}

type EventRecord = {
  id: string
  start: string
  end: string
  location: string
  municipality: string
  zone: string
  species: string
  losses: string
  economicLoss: string
  cause: string
  sourceTitle: string
  sourceUrl: string
  publicationDate: string
  datePrecision: string
  locationPrecision: string
  verification: string
  notes: string
}

type AuditRecord = {
  id: string
  claim: string
  source: string
  locator: string
  issue: string
  decision: string
  reason: string
}

type SourceRecord = {
  id: string
  filename: string
  type: string
  organization: string
  publication: string
  period: string
  content: string
  incidents: string
  labels: string
  used: string
}

type CheckRecord = {
  check: string
  requirement: string
  status: string
  evidence: string
}

type ReadinessRecord = CheckRecord & {
  consequence: string
}

type RealTrendTarget = {
  label: string
  unit: string
  n: number
  nStations: number
  slopePerYear: number
  ciLow: number
  ciHigh: number
  standardError: number
  bootstrapLow: number | null
  bootstrapHigh: number | null
  bootstrapReps: number
  rSquared: number | null
  direction: string
  interpretation: string
}

type RealAlignment = {
  generatedAtUtc: string
  status: string
  modelType: string
  fishKillPrediction: boolean
  warning: string
  panel: {
    stations: number
    stationNames: string[]
    years: string
    nYears: number
  }
  targets: {
    do: RealTrendTarget
    temperature: RealTrendTarget
  }
  method: string
  caveat: string
  unsupported: {
    target: string
    status: string
    reasons: string[]
  }
}

type DashboardData = {
  generatedAtUtc: string
  project: {
    name: string
    subtitle: string
    studyArea: string
    status: string
    dataDates: string
  }
  coverage: {
    lakeStations: number
    lakeStationYears: number
    completeStationYears: number
    numericWaterQualityValues: number
    datedWaterQualityRows: number
    rainNumericMonths: number
    windNumericMonths: number
    sourceCount: number
    eventReports: number
    verifiedEvents: number
    lakeStationsWithZoneLabel: number
  }
  metrics: Metric[]
  realAlignment: RealAlignment
  waterQuality: {
    variables: WaterVariable[]
    stations: Array<{
      name: string
      zone: string
      firstYear: number | null
      lastYear: number | null
      numericYears: number | null
      variables: string
      zoneEvidence: string
    }>
    measurements: Measurement[]
    note: string
  }
  weather: {
    rainfall: { years: YearPoint[]; latest: YearPoint | null; unit: string }
    wind: { years: YearPoint[]; latest: YearPoint | null; unit: string }
    lakeArea: {
      stationName: string
      sourceId: string
      role: string
      years: RainfallYear[]
      latest: RainfallYear | null
      partial2025: {
        year: number
        total: number | null
        months: number
        note: string
      }
      monthly: MonthlyRainfall[]
      note: string
    }
    note: string
  }
  events: EventRecord[]
  evidenceAudit: AuditRecord[]
  sources: SourceRecord[]
  dataRequests: {
    total: number
    acknowledged: number
    planned: number
    received: number
    files: number
    outreachPaused: boolean
    note: string
  }
  figures: Array<{ file: string; title: string; caption: string }>
  governance: {
    feasibility: Record<string, string | number | null>
    readiness: ReadinessRecord[]
    trainingChecks: CheckRecord[]
    evaluationChecks: CheckRecord[]
    modelStatus: string
    metricsAvailable: boolean
    realTrendAvailable: boolean
  }
  risk: {
    status: string
    headline: string
    summary: string
    reasons: string[]
  }
}

const data = dashboardJson as unknown as DashboardData

const PAGE_META: Record<
  PageId,
  { index: string; label: string; title: string; intro: string }
> = {
  overview: {
    index: "01",
    label: "Overview",
    title: "What the data can — and cannot — tell us",
    intro:
      "A source-reviewed evidence dashboard for Laguna de Bay water quality, weather, and a reported 2019 fish kill.",
  },
  water: {
    index: "02",
    label: "Water data",
    title: "Water and weather, 2016–2025",
    intro:
      "Annual lake-station summaries and monthly weather records. These describe long-term conditions; they are not daily or live measurements.",
  },
  evidence: {
    index: "03",
    label: "Fish-kill evidence",
    title: "One reported event, examined",
    intro:
      "The incident record, its source trail, and the claims that were excluded before the event dataset was built.",
  },
  model: {
    index: "04",
    label: "Model run",
    title: "Synthetic model run and real-data boundary",
    intro:
      "A 24/48/72-hour fish-kill model has been trained on the synthetic gap-filled database. The real-data risk assessment remains unavailable.",
  },
  sources: {
    index: "05",
    label: "Sources",
    title: "The evidence base",
    intro:
      "Fourteen supplied files, their coverage, and the precise role each one plays in the research prototype.",
  },
}

const NAV_ITEMS: Array<{ id: PageId; label: string; index: string }> = [
  { id: "overview", label: PAGE_META.overview.label, index: PAGE_META.overview.index },
  { id: "water", label: PAGE_META.water.label, index: PAGE_META.water.index },
  { id: "evidence", label: PAGE_META.evidence.label, index: PAGE_META.evidence.index },
  { id: "model", label: PAGE_META.model.label, index: PAGE_META.model.index },
  { id: "sources", label: PAGE_META.sources.label, index: PAGE_META.sources.index },
]

const SOURCE_TYPE_LABELS: Record<string, string> = {
  xlsx: "Excel workbook",
  pdf: "PDF",
  docx: "Word document",
  zip: "UI archive",
  md: "Web article",
}

const SOURCE_TYPE_PLURALS: Record<string, string> = {
  xlsx: "Excel workbooks",
  pdf: "PDFs",
  docx: "Word documents",
  zip: "UI archives",
  md: "Web articles",
}

const MONTHS = [
  "Jan",
  "Feb",
  "Mar",
  "Apr",
  "May",
  "Jun",
  "Jul",
  "Aug",
  "Sep",
  "Oct",
  "Nov",
  "Dec",
]

const sourceTypeCounts = data.sources.reduce<Record<string, number>>(
  (counts, source) => {
    counts[source.type] = (counts[source.type] ?? 0) + 1
    return counts
  },
  {},
)

const event = data.events[0]

const WATER_YEARS = Array.from(
  new Set(data.waterQuality.measurements.map((measurement) => measurement.year)),
).sort((left, right) => left - right)

const LATEST_WATER_YEAR = WATER_YEARS[WATER_YEARS.length - 1] ?? 2025

const DEFAULT_VARIABLE_KEY =
  data.waterQuality.variables.find(
    (variable) => variable.key === "Dissolved oxygen (DO)",
  )?.key ??
  data.waterQuality.variables[0]?.key ??
  ""

const READINESS_COUNTS = data.governance.readiness.reduce<Record<string, number>>(
  (counts, check) => {
    counts[check.status] = (counts[check.status] ?? 0) + 1
    return counts
  },
  {},
)

function shortVariableLabel(label: string): string {
  return label.replace(" (DO)", "").replace("Water temperature", "Temperature")
}

function formatNumber(value: number | null | undefined, digits = 2): string {
  if (value === null || value === undefined || !Number.isFinite(value)) {
    return "—"
  }

  return value.toLocaleString("en-US", {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  })
}

function displayUnit(unit: string): string {
  return unit === "deg C" ? "°C" : unit
}

function formatWithUnit(value: number | null | undefined, unit: string): string {
  return `${formatNumber(value)} ${displayUnit(unit)}`
}

function parseDate(value: string): Date | null {
  const date = new Date(`${value}T00:00:00Z`)
  return Number.isNaN(date.getTime()) ? null : date
}

function formatDate(value: string): string {
  const date = parseDate(value)
  if (!date) return value
  return `${date.getUTCDate()} ${MONTHS[date.getUTCMonth()]} ${date.getUTCFullYear()}`
}

function formatDateRange(start: string, end: string): string {
  const startDate = parseDate(start)
  const endDate = parseDate(end)
  if (!startDate || !endDate) return `${start} – ${end}`

  if (
    startDate.getUTCFullYear() === endDate.getUTCFullYear() &&
    startDate.getUTCMonth() === endDate.getUTCMonth()
  ) {
    return `${startDate.getUTCDate()}–${endDate.getUTCDate()} ${
      MONTHS[startDate.getUTCMonth()]
    } ${startDate.getUTCFullYear()}`
  }

  return `${formatDate(start)} – ${formatDate(end)}`
}

function readPageFromHash(): PageId {
  const hash = window.location.hash.replace(/^#\/?/, "")
  return NAV_ITEMS.some((item) => item.id === hash)
    ? (hash as PageId)
    : "overview"
}

function slugify(value: string): string {
  return value
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "_")
    .replace(/^_+|_+$/g, "")
}

function downloadVariableCsv(variable: WaterVariable): void {
  const rows = data.waterQuality.measurements.filter(
    (measurement) => measurement.variable === variable.key,
  )

  const quote = (value: string | number): string =>
    `"${String(value).replace(/"/g, '""')}"`

  const header = [
    "station",
    "zone",
    "year",
    "variable",
    "value",
    "unit",
    "quality_flag",
  ]
  const csv = [
    header.map(quote).join(","),
    ...rows.map((row) =>
      [
        row.station,
        row.zone,
        row.year,
        row.variable,
        row.value,
        row.unit,
        row.quality,
      ]
        .map(quote)
        .join(","),
    ),
  ].join("\r\n")

  const blob = new Blob([`\ufeff${csv}`], {
    type: "text/csv;charset=utf-8;",
  })
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement("a")
  anchor.href = url
  anchor.download = `himpil_${slugify(variable.label)}_annual.csv`
  document.body.appendChild(anchor)
  anchor.click()
  anchor.remove()
  window.setTimeout(() => URL.revokeObjectURL(url), 0)
}

function Badge({
  children,
  tone = "neutral",
}: {
  children: ReactNode
  tone?: "neutral" | "positive" | "warning" | "danger"
}) {
  return <span className={`badge badge--${tone}`}>{children}</span>
}

function StatusBadge({ status }: { status: string }) {
  if (status === "pass") {
    return <Badge tone="positive">Met</Badge>
  }
  if (status === "partial") {
    return <Badge tone="warning">Partial</Badge>
  }
  return <Badge tone="danger">Not met</Badge>
}

function PageHeading({
  index,
  label,
  title,
  intro,
  actions,
}: {
  index: string
  label: string
  title: string
  intro: string
  actions?: ReactNode
}) {
  return (
    <header className="page-heading">
      <div className="page-heading__copy">
        <p className="eyebrow">
          <span>{index}</span>
          {label} / HIMPIL
        </p>
        <h1>{title}</h1>
        <p className="page-intro">{intro}</p>
      </div>
      {actions ? <div className="page-actions">{actions}</div> : null}
    </header>
  )
}

function SectionRule({
  number,
  title,
  note,
}: {
  number: string
  title: string
  note?: string
}) {
  return (
    <div className="section-rule">
      <span className="section-rule__number">{number}</span>
      <h2>{title}</h2>
      {note ? <p>{note}</p> : null}
    </div>
  )
}

function PanelHeading({
  id,
  title,
  description,
  aside,
}: {
  id?: string
  title: string
  description?: string
  aside?: ReactNode
}) {
  return (
    <div className="panel-heading">
      <div>
        <h2 id={id}>{title}</h2>
        {description ? <p>{description}</p> : null}
      </div>
      {aside ? <div className="panel-heading__aside">{aside}</div> : null}
    </div>
  )
}

function Notice({
  title,
  children,
  action,
  tone = "warning",
}: {
  title: string
  children: ReactNode
  action?: ReactNode
  tone?: "warning" | "danger" | "info"
}) {
  return (
    <section className={`notice notice--${tone}`} aria-labelledby="notice-title">
      <span className="notice__mark" aria-hidden="true">
        !
      </span>
      <div className="notice__body">
        <h2 id="notice-title">{title}</h2>
        {children}
      </div>
      {action ? <div className="notice__action">{action}</div> : null}
    </section>
  )
}

function StatCard({
  value,
  label,
  note,
  tone = "default",
}: {
  value: ReactNode
  label: string
  note: string
  tone?: "default" | "warning"
}) {
  return (
    <div className={`stat-card${tone === "warning" ? " stat-card--warning" : ""}`}>
      <span className="stat-card__label">{label}</span>
      <strong className="stat-card__value">{value}</strong>
      <span className="stat-card__note">{note}</span>
    </div>
  )
}

function Sparkline({
  points,
  label,
}: {
  points: Array<number | null>
  label: string
}) {
  const numeric = points.filter(
    (point): point is number => typeof point === "number" && Number.isFinite(point),
  )

  if (numeric.length < 2) {
    return <span className="sparkline-empty">No trend values</span>
  }

  const width = 142
  const height = 38
  const padding = 3
  const minimum = Math.min(...numeric)
  const maximum = Math.max(...numeric)
  const span = maximum - minimum || 1

  const coordinates = points.map((point, index) => {
    if (typeof point !== "number" || !Number.isFinite(point)) return null
    return {
      x: padding + (index / Math.max(1, points.length - 1)) * (width - padding * 2),
      y:
        height -
        padding -
        ((point - minimum) / span) * (height - padding * 2),
    }
  })

  let path = ""
  let drawing = false
  coordinates.forEach((point) => {
    if (!point) {
      drawing = false
      return
    }
    path += `${drawing ? " L" : " M"} ${point.x.toFixed(1)} ${point.y.toFixed(1)}`
    drawing = true
  })

  const lastPoint = coordinates.reduce<{ x: number; y: number } | null>(
    (last, point) => point ?? last,
    null,
  )

  return (
    <svg
      className="sparkline"
      viewBox={`0 0 ${width} ${height}`}
      role="img"
      aria-label={label}
    >
      <path d={path.trim()} fill="none" />
      {lastPoint ? (
        <circle cx={lastPoint.x} cy={lastPoint.y} r="2.6" />
      ) : null}
    </svg>
  )
}

function MetricCard({ metric }: { metric: Metric }) {
  const year = metric.period.match(/\b20\d{2}\b/)?.[0]

  return (
    <article className="metric-card">
      <div className="metric-card__top">
        <h3>{metric.label}</h3>
        {year ? <span className="metric-year">{year}</span> : null}
      </div>
      <p className="metric-value">
        {metric.display}
        <span>{displayUnit(metric.unit)}</span>
      </p>
      <Sparkline
        points={metric.points}
        label={`Annual network means for ${metric.label}`}
      />
      <p className="metric-period">{metric.period}</p>
      <p className="metric-detail">{metric.detail}</p>
      <p className="metric-note">{metric.note}</p>
    </article>
  )
}

type ChartPoint = { x: number; y: number }

function pathFrom(points: Array<ChartPoint | null>): string {
  let path = ""
  let drawing = false

  points.forEach((point) => {
    if (!point) {
      drawing = false
      return
    }
    path += `${drawing ? " L" : " M"} ${point.x.toFixed(1)} ${point.y.toFixed(1)}`
    drawing = true
  })

  return path.trim()
}

function AnnualChart({ variable }: { variable: WaterVariable }) {
  const years = variable.years
  const values = years.flatMap((point) =>
    [point.mean, point.min, point.max].filter(
      (value): value is number => typeof value === "number",
    ),
  )

  if (years.length === 0 || values.length === 0) {
    return <p className="empty-state">No numeric annual values are available.</p>
  }

  const width = 760
  const height = 310
  const margin = { top: 24, right: 24, bottom: 44, left: 58 }
  const plotWidth = width - margin.left - margin.right
  const plotHeight = height - margin.top - margin.bottom

  const minimum = Math.min(...values)
  const maximum = Math.max(...values)
  const rangePadding = (maximum - minimum || 1) * 0.14
  const lower = minimum - rangePadding
  const upper = maximum + rangePadding

  const xFor = (index: number): number =>
    margin.left +
    (years.length === 1 ? plotWidth / 2 : (index / (years.length - 1)) * plotWidth)
  const yFor = (value: number): number =>
    margin.top + ((upper - value) / (upper - lower)) * plotHeight

  const meanPoints = years.map((point, index) =>
    point.mean === null ? null : { x: xFor(index), y: yFor(point.mean) },
  )
  const minPoints = years.map((point, index) =>
    point.min === null ? null : { x: xFor(index), y: yFor(point.min) },
  )
  const maxPoints = years.map((point, index) =>
    point.max === null ? null : { x: xFor(index), y: yFor(point.max) },
  )

  const hasCompleteBand = years.every(
    (point) => point.min !== null && point.max !== null,
  )
  let bandPath = ""
  if (hasCompleteBand) {
    const top = maxPoints
      .map((point) => `${point?.x.toFixed(1)},${point?.y.toFixed(1)}`)
      .join(" L ")
    const bottom = [...minPoints]
      .reverse()
      .map((point) => `${point?.x.toFixed(1)},${point?.y.toFixed(1)}`)
      .join(" L ")
    bandPath = `M ${top} L ${bottom} Z`
  }

  const yTicks = Array.from({ length: 5 }, (_, index) => {
    const value = lower + ((upper - lower) * index) / 4
    return { value, y: yFor(value) }
  })

  return (
    <figure className="chart-figure">
      <div className="chart-legend" aria-hidden="true">
        <span>
          <i className="legend-swatch legend-swatch--mean" /> Network mean
        </span>
        <span>
          <i className="legend-swatch legend-swatch--range" /> Station minimum–maximum
        </span>
      </div>
      <div className="chart-scroll">
        <svg
          className="annual-chart"
          viewBox={`0 0 ${width} ${height}`}
          role="img"
          aria-label={`Annual ${variable.label} summaries for Laguna de Bay lake stations`}
        >
          <title>{variable.label} annual network summary</title>
          <desc>
            Annual network mean with the minimum and maximum station values for
            each year. Values are annual station summaries, not daily readings.
          </desc>

          {yTicks.map((tick) => (
            <g key={tick.value}>
              <line
                className="chart-grid"
                x1={margin.left}
                x2={width - margin.right}
                y1={tick.y}
                y2={tick.y}
              />
              <text
                className="chart-axis-text"
                x={margin.left - 10}
                y={tick.y + 4}
                textAnchor="end"
              >
                {formatNumber(tick.value)}
              </text>
            </g>
          ))}

          {bandPath ? <path className="chart-band" d={bandPath} /> : null}
          <path className="chart-line chart-line--range" d={pathFrom(maxPoints)} />
          <path className="chart-line chart-line--range" d={pathFrom(minPoints)} />
          <path className="chart-line chart-line--mean" d={pathFrom(meanPoints)} />

          {years.map((point, index) => (
            <g key={point.year}>
              <text
                className="chart-axis-text"
                x={xFor(index)}
                y={height - 16}
                textAnchor="middle"
              >
                {point.year}
              </text>
              {point.mean !== null ? (
                <circle
                  className="chart-dot"
                  cx={xFor(index)}
                  cy={yFor(point.mean)}
                  r="3.4"
                >
                  <title>
                    {point.year}: {formatWithUnit(point.mean, variable.unit)} mean;{" "}
                    {point.n} station{point.n === 1 ? "" : "s"} reporting
                  </title>
                </circle>
              ) : null}
            </g>
          ))}

          <text
            className="chart-axis-title"
            x={margin.left}
            y={12}
            textAnchor="start"
          >
            {displayUnit(variable.unit)}
          </text>
        </svg>
      </div>
      <figcaption>
        Each point is the mean of reported annual station summaries for that
        year. Shading spans the station minimum and maximum. No regulatory
        threshold is applied because the source values are annual summaries.
      </figcaption>
    </figure>
  )
}

function RealTrendPanel() {
  const trend = data.realAlignment
  const doTrend = trend.targets.do
  const tempTrend = trend.targets.temperature

  return (
    <section className="panel" aria-labelledby="real-trend-title">
      <PanelHeading
        id="real-trend-title"
        title="What the annual data can support"
        description="A descriptive annual trend model on a balanced nine-station panel. It is not a fish-kill prediction."
        aside={<Badge tone="neutral">Descriptive only</Badge>}
      />
      <p className="panel-lead">
        This is the only real model fitted in the current system. It summarizes
        within-station change in annual mean dissolved oxygen and water
        temperature. It does not create a fish-kill label or a 72-hour warning.
      </p>

      <div
        className="stats-grid stats-grid--three"
        aria-label="Annual trend estimates"
      >
        <StatCard
          value={`${formatNumber(doTrend.slopePerYear, 3)} mg/L`}
          label="DO change per year"
          note={`95% CI ${formatNumber(doTrend.ciLow, 3)} to ${formatNumber(
            doTrend.ciHigh,
            3,
          )}; ${doTrend.n} station-years`}
        />
        <StatCard
          value={`${formatNumber(tempTrend.slopePerYear, 3)} ${displayUnit(
            "deg C",
          )}`}
          label="Temperature change per year"
          note={`95% CI ${formatNumber(tempTrend.ciLow, 3)} to ${formatNumber(
            tempTrend.ciHigh,
            3,
          )}; ${tempTrend.n} station-years`}
        />
        <StatCard
          value={trend.panel.stations}
          label="Balanced panel"
          note={`${trend.panel.years}; station fixed effects`}
        />
      </div>

      <div className="two-column two-column--equal">
        <div>
          <h3>Dissolved oxygen</h3>
          <p>
            {doTrend.interpretation} The estimate is a descriptive
            association, not a causal finding.
          </p>
        </div>
        <div>
          <h3>Water temperature</h3>
          <p>
            {tempTrend.interpretation} The interval is wide, so the direction
            is not established.
          </p>
        </div>
      </div>

      <p className="fine-print">
        <strong>Descriptive annual trend only.</strong> Not a fish-kill
        prediction and not a substitute for the trained synthetic 72-hour run.
      </p>
      <p className="fine-print">{trend.caveat}</p>

      <div className="two-column two-column--equal">
        <div>
          <h3>72-hour prediction from annual real data</h3>
          <p>
            <Badge tone="warning">Real data only</Badge>
          </p>
          <p>
            The supplied annual real data cannot support a validated 72-hour
            fish-kill model. The separate synthetic 24/48/72-hour run is on the
            Model run page.
          </p>
        </div>
        <div>
          <h3>Why the 72-hour target is blocked</h3>
          <ul className="plain-list plain-list--unsupported">
            {trend.unsupported.reasons.map((reason) => (
              <li key={reason}>{reason}</li>
            ))}
          </ul>
        </div>
      </div>

      <p className="fine-print">
        The real-data fish-kill risk state remains{" "}
        <strong>risk assessment unavailable</strong>. This trend panel does not
        change that state, and the synthetic run is tracked separately.
      </p>
    </section>
  )
}

function SeriesChart({
  points,
  unit,
  label,
  digits = 2,
}: {
  points: YearPoint[]
  unit: string
  label: string
  digits?: number
}) {
  const available = points.filter(
    (point): point is YearPoint & { mean: number } =>
      typeof point.mean === "number" && Number.isFinite(point.mean),
  )

  if (available.length < 2) {
    return <p className="empty-state">No multi-year series is available.</p>
  }

  const width = 560
  const height = 210
  const margin = { top: 20, right: 18, bottom: 36, left: 52 }
  const plotWidth = width - margin.left - margin.right
  const plotHeight = height - margin.top - margin.bottom
  const values = available.map((point) => point.mean)
  const minimum = Math.min(...values)
  const maximum = Math.max(...values)
  const padding = (maximum - minimum || 1) * 0.16
  const lower = minimum - padding
  const upper = maximum + padding

  const xFor = (index: number): number =>
    margin.left +
    (points.length === 1 ? plotWidth / 2 : (index / (points.length - 1)) * plotWidth)
  const yFor = (value: number): number =>
    margin.top + ((upper - value) / (upper - lower)) * plotHeight

  const coordinates = points.map((point, index) =>
    point.mean === null ? null : { x: xFor(index), y: yFor(point.mean) },
  )

  const yTicks = Array.from({ length: 4 }, (_, index) => {
    const value = lower + ((upper - lower) * index) / 3
    return { value, y: yFor(value) }
  })

  return (
    <div className="series-chart-scroll">
      <svg
        className="series-chart"
        viewBox={`0 0 ${width} ${height}`}
        role="img"
        aria-label={label}
      >
        <title>{label}</title>
        {yTicks.map((tick) => (
          <g key={tick.value}>
            <line
              className="chart-grid"
              x1={margin.left}
              x2={width - margin.right}
              y1={tick.y}
              y2={tick.y}
            />
            <text
              className="chart-axis-text"
              x={margin.left - 9}
              y={tick.y + 4}
              textAnchor="end"
            >
              {formatNumber(tick.value, digits)}
            </text>
          </g>
        ))}

        <path className="chart-line chart-line--mean" d={pathFrom(coordinates)} />

        {points.map((point, index) => (
          <g key={point.year}>
            <text
              className="chart-axis-text"
              x={xFor(index)}
              y={height - 13}
              textAnchor="middle"
            >
              {point.year}
            </text>
            {point.mean !== null ? (
              <circle
                className="chart-dot"
                cx={xFor(index)}
                cy={yFor(point.mean)}
                r="3.2"
              >
                <title>
                  {point.year}: {formatNumber(point.mean, digits)} {displayUnit(unit)}
                </title>
              </circle>
            ) : null}
          </g>
        ))}

        <text
          className="chart-axis-title"
          x={margin.left}
          y={11}
          textAnchor="start"
        >
          {displayUnit(unit)}
        </text>
      </svg>
    </div>
  )
}

function LakeAreaRainfall() {
  const lake = data.weather.lakeArea
  const latest = lake.latest
  const annualPoints: YearPoint[] = lake.years.map((point) => ({
    year: point.year,
    n: 1,
    mean: point.total,
    min: null,
    max: null,
  }))
  const maxMonthly = Math.max(...lake.monthly.map((month) => month.mean), 1)
  const partial = lake.partial2025

  return (
    <article className="lake-rainfall" aria-labelledby="lake-rainfall-title">
      <div className="lake-rainfall__head">
        <div>
          <p className="section-kicker">Lake-area station</p>
          <h3 id="lake-rainfall-title">{lake.stationName}</h3>
          <p className="fine-print">{lake.role}</p>
        </div>
        <span className="data-stamp">{lake.sourceId}</span>
      </div>

      <div className="lake-rainfall__grid">
        <div className="lake-rainfall__annual">
          <p className="section-kicker">Latest complete year</p>
          <p className="weather-value">
            {latest ? formatNumber(latest.total, 1) : "—"}
            <span>mm/year</span>
          </p>
          <p className="weather-meta">
            {latest
              ? `${latest.year} · ${latest.months} months`
              : "No complete year available"}
          </p>
          <SeriesChart
            points={annualPoints}
            unit="mm/year"
            label="Tanay annual rainfall totals, 2016 to 2024"
            digits={1}
          />
          <p className="fine-print">
            Annual totals from complete 12-month station-years. The partial 2025
            record is not plotted as an annual total.
          </p>
        </div>

        <div className="lake-rainfall__monthly">
          <p className="section-kicker">Monthly climatology, 2016–2024</p>
          <div
            className="monthly-bars"
            role="list"
            aria-label="Tanay mean monthly rainfall, 2016 to 2024"
          >
            {lake.monthly.map((month) => (
              <div
                className="monthly-bar"
                key={month.month}
                role="listitem"
                aria-label={`${month.label}: ${formatNumber(month.mean, 0)} mm mean; range ${formatNumber(month.min, 0)}–${formatNumber(month.max, 0)} mm across ${month.years} years`}
                title={`${month.label}: ${formatNumber(month.mean, 0)} mm mean; range ${formatNumber(month.min, 0)}–${formatNumber(month.max, 0)} mm across ${month.years} years`}
              >
                <div className="monthly-bar__track">
                  <div
                    className="monthly-bar__fill"
                    style={{
                      height: `${Math.max(2, (month.mean / maxMonthly) * 100)}%`,
                    }}
                  />
                </div>
                <span className="monthly-bar__value">
                  {formatNumber(month.mean, 0)}
                </span>
                <span className="monthly-bar__label">{month.label}</span>
              </div>
            ))}
          </div>
          <p className="fine-print">
            Mean of nine complete years. The wet season is a descriptive feature
            of this station, not a risk rule.
          </p>
        </div>
      </div>

      <div className="lake-rainfall__footer">
        <p className="fine-print">{lake.note}</p>
        {partial.total !== null ? (
          <p className="fine-print">
            <strong>Partial {partial.year}:</strong>{" "}
            {formatNumber(partial.total, 2)} mm over {partial.months} months.{" "}
            {partial.note}
          </p>
        ) : null}
      </div>
    </article>
  )
}

function WeatherSection() {
  const series = [
    {
      id: "rainfall",
      label: "Network rainfall",
      kicker: "PAGASA network mean",
      unit: data.weather.rainfall.unit,
      points: data.weather.rainfall.years,
      latest: data.weather.rainfall.latest,
      digits: 0,
      note: "Mean of complete 12-month station-years across the supplied PAGASA network. This is not lake-specific. The provisional 2025 data are excluded.",
    },
    {
      id: "wind",
      label: "Network wind speed",
      kicker: "PAGASA network mean",
      unit: data.weather.wind.unit,
      points: data.weather.wind.years,
      latest: data.weather.wind.latest,
      digits: 2,
      note: "Station means require 12 numeric months. This is a network summary, not a lake measurement. The provisional 2025 data are excluded.",
    },
  ]

  return (
    <section className="panel weather-panel" aria-labelledby="weather-title">
      <PanelHeading
        id="weather-title"
        title="Weather context"
        description="Monthly PAGASA records rolled up to complete station-years. The network cards describe all supplied stations; the Tanay card is the only clearly lake-area station. These provide environmental context, not a forecast input."
        aside={<span className="data-stamp">2016–2024</span>}
      />
      <div className="weather-grid">
        {series.map((item) => (
          <article className="weather-card" key={item.id}>
            <div className="weather-card__head">
              <div>
                <p className="section-kicker">{item.kicker}</p>
                <h3>{item.label}</h3>
              </div>
              <span className="weather-year">{item.latest?.year ?? "—"}</span>
            </div>
            <p className="weather-value">
              {item.latest ? formatNumber(item.latest.mean, item.digits) : "—"}
              <span>{item.unit}</span>
            </p>
            <p className="weather-meta">
              {item.latest
                ? `${item.latest.n} stations with complete records`
                : "No complete year available"}
            </p>
            <SeriesChart
              points={item.points}
              unit={item.unit}
              label={`${item.label} by year, PAGASA station network`}
              digits={item.digits}
            />
            <p className="fine-print">{item.note}</p>
          </article>
        ))}
      </div>
      <LakeAreaRainfall />
      <p className="fine-print">{data.weather.note}</p>
    </section>
  )
}

function AnalysisGallery() {
  const figures = data.figures

  if (figures.length === 0) return null

  return (
    <section className="analysis-section" aria-labelledby="analysis-title">
      <div className="analysis-section__intro">
        <p className="eyebrow">Supporting analysis / R</p>
        <h2 id="analysis-title">Plates from the analysis workflow</h2>
        <p>
          Completeness and distribution checks generated from the documented
          CSVs. They support the same descriptive reading as the dashboard
          charts; they do not add a prediction.
        </p>
      </div>
      <div className="figure-grid">
        {figures.map((figure) => (
          <figure className="analysis-figure" key={figure.file}>
            <img
              src={`/${figure.file}`}
              alt={`${figure.title}. ${figure.caption}`}
            />
            <figcaption>
              <span>{figure.title}</span>
              <p>{figure.caption}</p>
            </figcaption>
          </figure>
        ))}
      </div>
    </section>
  )
}

function EvidenceLadder() {
  const steps = [
    {
      state: "complete",
      number: "01",
      title: "Reported",
      note: "UP Diliman article",
    },
    {
      state: "complete",
      number: "02",
      title: "Traceable",
      note: "Named institutional source",
    },
    {
      state: "missing",
      number: "03",
      title: "Corroborated",
      note: "No second source",
    },
    {
      state: "missing",
      number: "04",
      title: "Officially verified",
      note: "No formal report supplied",
    },
  ]

  return (
    <ol className="evidence-ladder" aria-label="Verification ladder">
      {steps.map((step) => (
        <li className={`evidence-step evidence-step--${step.state}`} key={step.number}>
          <span className="evidence-step__number">{step.number}</span>
          <strong>{step.title}</strong>
          <small>{step.note}</small>
        </li>
      ))}
    </ol>
  )
}

function DashKpi({
  value,
  label,
  note,
  tone = "default",
}: {
  value: ReactNode
  label: string
  note: string
  tone?: "default" | "warning"
}) {
  return (
    <article className={`dash-kpi${tone === "warning" ? " dash-kpi--warning" : ""}`}>
      <span className="dash-kpi__label">{label}</span>
      <strong className="dash-kpi__value">{value}</strong>
      <span className="dash-kpi__note">{note}</span>
    </article>
  )
}

function ReadinessDonut({
  pass,
  partial,
  fail,
}: {
  pass: number
  partial: number
  fail: number
}) {
  const total = pass + partial + fail
  const radius = 38
  const circumference = 2 * Math.PI * radius
  const segments = [
    { value: pass, color: "var(--green)" },
    { value: partial, color: "var(--amber)" },
    { value: fail, color: "var(--red)" },
  ]
  let cursor = 0

  return (
    <svg
      className="readiness-donut"
      viewBox="0 0 100 100"
      role="img"
      aria-label={`${pass} of ${total} readiness checks fully met; ${partial} partial; ${fail} not met`}
    >
      <circle
        cx="50"
        cy="50"
        r={radius}
        fill="none"
        stroke="var(--paper-deep)"
        strokeWidth="11"
      />
      {segments.map((segment, index) => {
        if (segment.value === 0 || total === 0) return null
        const length = (segment.value / total) * circumference
        const gap = total > 1 ? 1.8 : 0
        const rotation = (cursor / total) * 360 - 90
        cursor += segment.value
        return (
          <circle
            key={index}
            cx="50"
            cy="50"
            r={radius}
            fill="none"
            stroke={segment.color}
            strokeWidth="11"
            strokeDasharray={`${Math.max(0, length - gap)} ${circumference}`}
            transform={`rotate(${rotation} 50 50)`}
          />
        )
      })}
      <text x="50" y="48" textAnchor="middle" className="readiness-donut__value">
        {pass}/{total}
      </text>
      <text x="50" y="60" textAnchor="middle" className="readiness-donut__label">
        met
      </text>
    </svg>
  )
}

function RequestBar({
  label,
  value,
  total,
  tone,
}: {
  label: string
  value: number
  total: number
  tone: "accent" | "muted" | "warning"
}) {
  const width = total > 0 ? Math.min(100, (value / total) * 100) : 0

  return (
    <div className="dash-bar">
      <div className="dash-bar__top">
        <span>{label}</span>
        <strong>{value}</strong>
      </div>
      <div className="dash-bar__track" aria-hidden="true">
        <span
          className={`dash-bar__fill dash-bar__fill--${tone}`}
          style={{ width: `${width}%` }}
        />
      </div>
    </div>
  )
}

function OverviewHero() {
  return (
    <header className="dash-hero">
      <div className="dash-hero__copy">
        <p className="eyebrow">
          <span>01</span>
          Evidence review / Laguna de Bay
        </p>
        <h1>{PAGE_META.overview.title}</h1>
        <p className="dash-hero__intro">{PAGE_META.overview.intro}</p>
        <div className="dash-hero__meta" aria-label="Project scope">
          <span>{data.project.studyArea}</span>
          <span>{data.coverage.lakeStations} lake stations</span>
          <span>{data.coverage.sourceCount} supplied sources</span>
          <span>Build {formatDate(data.generatedAtUtc.slice(0, 10))}</span>
        </div>
      </div>

      <aside
        className="dash-hero__status"
        aria-labelledby="evidence-ticket-title"
      >
        <div className="dash-hero__status-label">
          <span>Synthetic experiment</span>
          <span className="dash-hero__dot" aria-hidden="true" />
        </div>
        <h2 id="evidence-ticket-title">Synthetic model trained</h2>
        <p>
          The 24/48/72-hour fish-kill model is trained on the synthetic
          gap-filled database. The real-data risk assessment remains
          unavailable.
        </p>
        <dl className="dash-hero__facts">
          <div>
            <dt>Synthetic model</dt>
            <dd>Trained</dd>
          </div>
          <div>
            <dt>Real events</dt>
            <dd>{data.coverage.verifiedEvents}</dd>
          </div>
          <div>
            <dt>Dated water rows</dt>
            <dd>{data.coverage.datedWaterQualityRows}</dd>
          </div>
        </dl>
        <a className="text-link" href="#model">
          Review the model run →
        </a>
      </aside>
    </header>
  )
}

function OverviewPage() {
  const [selectedVariableKey, setSelectedVariableKey] = useState(DEFAULT_VARIABLE_KEY)
  const [selectedYear, setSelectedYear] = useState(LATEST_WATER_YEAR)
  const [selectedStation, setSelectedStation] = useState("")

  const selectedVariable =
    data.waterQuality.variables.find(
      (variable) => variable.key === selectedVariableKey,
    ) ?? data.waterQuality.variables[0]

  const selectedStationRecord = data.waterQuality.stations.find(
    (station) => station.name === selectedStation,
  )

  const coverageRows = useMemo(() => {
    const byStation = new Map<string, Map<number, Set<string>>>()

    data.waterQuality.measurements.forEach((measurement) => {
      const stationYears =
        byStation.get(measurement.station) ?? new Map<number, Set<string>>()
      const variables =
        stationYears.get(measurement.year) ?? new Set<string>()
      variables.add(measurement.variable)
      stationYears.set(measurement.year, variables)
      byStation.set(measurement.station, stationYears)
    })

    return data.waterQuality.stations.map((station) => {
      const cells = WATER_YEARS.map(
        (year) => byStation.get(station.name)?.get(year)?.size ?? 0,
      )
      return {
        ...station,
        cells,
        completeYears: cells.filter((count) => count === 6).length,
      }
    })
  }, [])

  const selectedYearIndex = WATER_YEARS.indexOf(selectedYear)
  const selectedYearComplete =
    selectedYearIndex >= 0
      ? coverageRows.filter((row) => row.cells[selectedYearIndex] === 6)
          .length
      : 0

  const readinessTotal = data.governance.readiness.length
  const readinessPass = READINESS_COUNTS.pass ?? 0
  const readinessPartial = READINESS_COUNTS.partial ?? 0
  const readinessFail = READINESS_COUNTS.fail ?? 0

  return (
    <>
      <OverviewHero />

      <section className="dash-toolbar" aria-label="Year selector">
        <span className="dash-toolbar__label">Annual window</span>
        <div className="dash-year-row">
          {WATER_YEARS.map((year) => (
            <button
              type="button"
              className={`dash-year${selectedYear === year ? " is-active" : ""}`}
              onClick={() => setSelectedYear(year)}
              aria-pressed={selectedYear === year}
              key={year}
            >
              {year}
            </button>
          ))}
        </div>
        <span className="dash-toolbar__note">
          {selectedYearComplete} of {data.coverage.lakeStations} stations
          complete in {selectedYear}
        </span>
      </section>

      <div className="dash-layout">
        <aside className="dash-sidebar" aria-label="Dashboard filters">
          <section className="dash-side-card">
            <h2>Water variable</h2>
            <p>Choose the series shown in the annual trend.</p>
            <div
              className="dash-filter-list"
              role="group"
              aria-label="Water variable"
            >
              {data.waterQuality.variables.map((variable) => (
                <button
                  type="button"
                  className={`dash-filter${
                    variable.key === selectedVariable.key ? " is-active" : ""
                  }`}
                  onClick={() => setSelectedVariableKey(variable.key)}
                  aria-pressed={variable.key === selectedVariable.key}
                  key={variable.key}
                >
                  <span>{shortVariableLabel(variable.label)}</span>
                  <small>{variable.summary.n}</small>
                </button>
              ))}
            </div>
          </section>

          <section className="dash-side-card">
            <h2>Lake station</h2>
            <p>Highlight one row in the completeness map.</p>
            <select
              className="dash-select"
              value={selectedStation}
              onChange={(changeEvent) =>
                setSelectedStation(changeEvent.target.value)
              }
              aria-label="Highlight a lake station"
            >
              <option value="">All {data.coverage.lakeStations} stations</option>
              {data.waterQuality.stations.map((station) => (
                <option value={station.name} key={station.name}>
                  {station.name}
                </option>
              ))}
            </select>
            {selectedStationRecord ? (
              <div className="dash-station">
                <span className="dash-station__zone">
                  {selectedStationRecord.zone || "Lake zone not reported"}
                </span>
                <strong>
                  {selectedStationRecord.numericYears ?? "—"} numeric years
                </strong>
                <small>{selectedStationRecord.zoneEvidence}</small>
                <button
                  type="button"
                  className="dash-clear"
                  onClick={() => setSelectedStation("")}
                >
                  Clear station
                </button>
              </div>
            ) : (
              <p className="dash-side-note">
                Only {data.coverage.lakeStationsWithZoneLabel} of{" "}
                {data.coverage.lakeStations} station names carry a lake-zone
                label. No coordinates were supplied.
              </p>
            )}
          </section>

          <section className="dash-side-card">
            <h2>Coverage key</h2>
            <div className="dash-legend">
              <span>
                <i className="heat-swatch heat-swatch--0" /> Not reported
              </span>
              <span>
                <i className="heat-swatch heat-swatch--2" /> 1–2 of 6
              </span>
              <span>
                <i className="heat-swatch heat-swatch--4" /> 3–5 of 6
              </span>
              <span>
                <i className="heat-swatch heat-swatch--6" /> 6 of 6
              </span>
            </div>
            <p className="dash-side-note">
              Each cell counts reported variables in one station-year. A blank
              cell is not zero.
            </p>
          </section>
        </aside>

        <div className="dash-center">
          <section className="dash-kpis" aria-label="Coverage at a glance">
            <DashKpi
              value={data.coverage.lakeStations}
              label="Lake stations"
              note="Annual LLDA summaries, 2016–2025"
            />
            <DashKpi
              value={
                <>
                  {data.coverage.completeStationYears}
                  <span className="dash-kpi__denominator">
                    /{data.coverage.lakeStationYears}
                  </span>
                </>
              }
              label="Complete station-years"
              note="All six water-quality variables present"
            />
            <DashKpi
              value={data.coverage.eventReports}
              label="Reported events"
              note="May 2019 · Biñan and Pila"
            />
            <DashKpi
              value={data.coverage.verifiedEvents}
              label="Verified events"
              note="No second source or formal report"
              tone="warning"
            />
          </section>

          <section
            className="panel dash-panel dash-heatmap-panel"
            aria-labelledby="coverage-map-title"
          >
            <div className="panel-heading panel-heading--split">
              <div>
                <p className="section-kicker">Coverage / station-year</p>
                <h2 id="coverage-map-title">
                  Where the annual record is complete
                </h2>
                <p>
                  Six water-quality variables across 15 lake stations and ten
                  annual summaries. Select a year or station to inspect it.
                </p>
              </div>
              <div className="dash-heading-figure">
                <strong>
                  {selectedYearComplete}
                  <span>/{data.coverage.lakeStations}</span>
                </strong>
                <small>complete in {selectedYear}</small>
              </div>
            </div>

            <div className="heatmap-scroll">
              <table className="heatmap">
                <caption className="sr-only">
                  Reported water-quality variables by lake station and year.
                  Each cell counts the variables with a numeric annual summary.
                </caption>
                <thead>
                  <tr>
                    <th scope="col">Lake station</th>
                    {WATER_YEARS.map((year) => (
                      <th
                        scope="col"
                        key={year}
                        className={selectedYear === year ? "is-selected" : ""}
                      >
                        <button
                          type="button"
                          onClick={() => setSelectedYear(year)}
                          aria-pressed={selectedYear === year}
                        >
                          {year}
                        </button>
                      </th>
                    ))}
                    <th
                      scope="col"
                      className="heatmap__summary"
                      title="Years with all six variables"
                    >
                      6/6
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {coverageRows.map((row) => (
                    <tr
                      key={row.name}
                      className={
                        selectedStation === row.name ? "is-selected" : ""
                      }
                    >
                      <th scope="row">
                        <button
                          type="button"
                          onClick={() => setSelectedStation(row.name)}
                          aria-pressed={selectedStation === row.name}
                        >
                          {row.name}
                        </button>
                        <small>{row.zone || "Zone not reported"}</small>
                      </th>
                      {row.cells.map((count, index) => (
                        <td
                          key={WATER_YEARS[index]}
                          className={`heatmap__cell heatmap__cell--${count}${
                            selectedYear === WATER_YEARS[index]
                              ? " heatmap__cell--focus"
                              : ""
                          }`}
                          title={`${row.name}, ${WATER_YEARS[index]}: ${count} of 6 variables`}
                          aria-label={`${row.name}, ${WATER_YEARS[index]}: ${count} of 6 variables`}
                        >
                          {count === 0 ? "" : count}
                        </td>
                      ))}
                      <td className="heatmap__summary">{row.completeYears}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="heatmap-footer">
              <span>Cell = variables reported</span>
              <span>
                {data.coverage.completeStationYears} of{" "}
                {data.coverage.lakeStationYears} complete station-years
              </span>
            </div>
          </section>

          <section
            className="panel dash-panel dash-trend"
            aria-labelledby="trend-title"
          >
            <PanelHeading
              id="trend-title"
              title={`${selectedVariable.label} annual signal`}
              description="Annual network summaries for the selected variable. The line is not a forecast or a daily reading."
              aside={<Badge>{selectedVariable.unit}</Badge>}
            />
            <AnnualChart variable={selectedVariable} />
            <div className="panel-footer">
              <span>{selectedVariable.summary.n} station-year values</span>
              <a className="text-link" href="#water">
                Open the station matrix →
              </a>
            </div>
          </section>

          <section
            className="panel dash-panel dash-signals"
            aria-labelledby="latest-signals-title"
          >
            <PanelHeading
              id="latest-signals-title"
              title="Latest annual signals"
              description="2025 water quality and 2024 weather. Each value is an annual or monthly summary, not a live reading."
              aside={
                <span className="dash-panel-note">
                  {data.metrics.length} indicators
                </span>
              }
            />
            <div className="dash-signal-list">
              {data.metrics.map((metric) => (
                <div className="dash-signal" key={metric.id}>
                  <div className="dash-signal__identity">
                    <strong>{metric.label}</strong>
                    <small>{metric.period}</small>
                  </div>
                  <div className="dash-signal__value">
                    {metric.display}
                    <span>{displayUnit(metric.unit)}</span>
                  </div>
                  <div className="dash-signal__spark">
                    <Sparkline
                      points={metric.points}
                      label={`Annual network means for ${metric.label}`}
                    />
                  </div>
                  <p className="dash-signal__note" title={metric.detail}>
                    {metric.note}
                  </p>
                </div>
              ))}
            </div>
          </section>
        </div>

        <aside className="dash-rail" aria-label="Readiness and evidence status">
          <section
            className="panel dash-panel dash-readiness"
            aria-labelledby="readiness-title"
          >
            <PanelHeading
              id="readiness-title"
              title="Readiness gate"
              description="Ten model requirements, checked against the supplied evidence."
              aside={
                <Badge tone={readinessPass === readinessTotal ? "positive" : "warning"}>
                  {readinessPass} of {readinessTotal} met
                </Badge>
              }
            />
            <div className="dash-readiness__top">
              <ReadinessDonut
                pass={readinessPass}
                partial={readinessPartial}
                fail={readinessFail}
              />
              <div className="dash-readiness__copy">
                <strong>The gate remains closed</strong>
                <p>
                  No dated pre-event observations and no credible negative
                  windows are available for a real model.
                </p>
              </div>
            </div>
            <ul className="dash-legend-list">
              <li>
                <span>
                  <i style={{ background: "var(--green)" }} aria-hidden="true" />
                  Fully met
                </span>
                <strong>{readinessPass}</strong>
              </li>
              <li>
                <span>
                  <i style={{ background: "var(--amber)" }} aria-hidden="true" />
                  Partial
                </span>
                <strong>{readinessPartial}</strong>
              </li>
              <li>
                <span>
                  <i style={{ background: "var(--red)" }} aria-hidden="true" />
                  Not met
                </span>
                <strong>{readinessFail}</strong>
              </li>
            </ul>
            <a className="text-link dash-panel-link" href="#model">
              Inspect every check →
            </a>
          </section>

          <section
            className="panel dash-panel dash-requests"
            aria-labelledby="requests-title"
          >
            <PanelHeading
              id="requests-title"
              title="Data requests"
              description="Follow-up status from the request package."
              aside={<Badge tone="warning">Outreach paused</Badge>}
            />
            <div className="dash-bars">
              <RequestBar
                label="Acknowledged"
                value={data.dataRequests.acknowledged}
                total={data.dataRequests.total}
                tone="accent"
              />
              <RequestBar
                label="Planned"
                value={data.dataRequests.planned}
                total={data.dataRequests.total}
                tone="muted"
              />
              <RequestBar
                label="Files received"
                value={data.dataRequests.files}
                total={data.dataRequests.total}
                tone="warning"
              />
            </div>
            <p className="dash-note">{data.dataRequests.note}</p>
          </section>

          <section
            className="panel dash-panel dash-event"
            aria-labelledby="reported-event-title"
          >
            <div className="panel-heading panel-heading--split">
              <div>
                <p className="section-kicker">Reported event / {event.id}</p>
                <h2 id="reported-event-title">May 2019 fish kill</h2>
              </div>
              <Badge tone="warning">Not verified</Badge>
            </div>
            <dl className="dash-event__meta">
              <div>
                <dt>Location</dt>
                <dd>{event.location}</dd>
              </div>
              <div>
                <dt>Period</dt>
                <dd>{formatDateRange(event.start, event.end)}</dd>
              </div>
              <div>
                <dt>Species</dt>
                <dd>{event.species}</dd>
              </div>
              <div>
                <dt>Lake zone</dt>
                <dd className="muted-value">Not reported</dd>
              </div>
            </dl>
            <a className="text-link dash-panel-link" href="#evidence">
              Open the event record →
            </a>
          </section>

          <section
            className="panel dash-panel dash-boundary"
            aria-labelledby="boundaries-title"
          >
            <PanelHeading
              id="boundaries-title"
              title="The evidence boundary"
              description="The system is deliberately limited to what the files can support."
            />
            <h3 className="mini-heading">Supported here</h3>
            <ul className="plain-list plain-list--supported">
              <li>Compare annual water-quality summaries by station and year.</li>
              <li>Review the provenance of a reported fish-kill event.</li>
              <li>Inspect every failed model-readiness requirement.</li>
            </ul>
            <h3 className="mini-heading">Not supported here</h3>
            <ul className="plain-list plain-list--unsupported">
              <li>Daily or live environmental conditions.</li>
              <li>A fish-kill risk level or 24-hour forecast.</li>
              <li>A complete count of historical fish kills.</li>
              <li>Station or lake-zone assignment without coordinates.</li>
            </ul>
            <p className="fine-print">
              {data.coverage.sourceCount} supplied sources. Original files remain
              unchanged; processed data are stored separately.
            </p>
          </section>
        </aside>
      </div>
    </>
  )
}

function WaterPage() {
  const [selectedKey, setSelectedKey] = useState("Dissolved oxygen (DO)")
  const selected =
    data.waterQuality.variables.find((variable) => variable.key === selectedKey) ??
    data.waterQuality.variables[0]

  const years = selected.years
  const latest = selected.latest

  const matrix = useMemo(() => {
    const values = new Map<string, Map<number, number>>()

    data.waterQuality.measurements
      .filter((measurement) => measurement.variable === selected.key)
      .forEach((measurement) => {
        const stationValues =
          values.get(measurement.station) ?? new Map<number, number>()
        stationValues.set(measurement.year, measurement.value)
        values.set(measurement.station, stationValues)
      })

    return data.waterQuality.stations.map((station) => ({
      ...station,
      values: years.map((point) => values.get(station.name)?.get(point.year) ?? null),
    }))
  }, [selected.key, years])

  return (
    <>
      <PageHeading
        index={PAGE_META.water.index}
        label={PAGE_META.water.label}
        title={PAGE_META.water.title}
        intro={PAGE_META.water.intro}
        actions={
          <button
            className="button button--secondary"
            type="button"
            onClick={() => downloadVariableCsv(selected)}
            disabled={selected.summary.n === 0}
          >
            Download CSV
          </button>
        }
      />

      <section className="panel measure-panel" aria-labelledby="measure-title">
        <div className="measure-panel__head">
          <div>
            <h2 id="measure-title">Choose a water-quality measure</h2>
            <p>Six measures are available for the lake-station network.</p>
          </div>
          <span className="unit-note">Unit: {displayUnit(selected.unit)}</span>
        </div>
        <div className="segmented" role="group" aria-label="Water-quality measure">
          {data.waterQuality.variables.map((variable) => (
            <button
              type="button"
              key={variable.key}
              className={variable.key === selected.key ? "is-active" : ""}
              aria-pressed={variable.key === selected.key}
              onClick={() => setSelectedKey(variable.key)}
            >
              {variable.label === "Dissolved oxygen (DO)"
                ? "Dissolved oxygen"
                : variable.label}
            </button>
          ))}
        </div>
        <p className="fine-print">
          {data.waterQuality.note} Values are not imputed; gaps remain gaps.
        </p>
      </section>

      <section className="stats-grid stats-grid--four" aria-label={`${selected.label} summary`}>
        <StatCard
          value={formatWithUnit(latest?.mean, selected.unit)}
          label={`${latest?.year ?? "Latest"} network mean`}
          note={`${latest?.n ?? 0} of ${data.coverage.lakeStations} lake stations reported`}
        />
        <StatCard
          value={`${formatNumber(latest?.min)}–${formatNumber(latest?.max)}`}
          label={`${latest?.year ?? "Latest"} station range`}
          note={displayUnit(selected.unit)}
        />
        <StatCard
          value={years.length}
          label="Reporting years"
          note={
            years.length > 0
              ? `${years[0].year}–${years[years.length - 1].year}`
              : "No years reported"
          }
        />
        <StatCard
          value={selected.summary.n}
          label="Station-year values"
          note="Numeric annual values for this measure"
        />
      </section>

      <section className="panel" aria-labelledby="trend-title">
        <PanelHeading
          id="trend-title"
          title={`${selected.label} over time`}
          description="Network mean and station range by year. Missing years appear as gaps."
        />
        <AnnualChart variable={selected} />
      </section>

      <RealTrendPanel />

      <section className="panel" aria-labelledby="station-table-title">
        <PanelHeading
          id="station-table-title"
          title="Station values by year"
          description={`All values in ${displayUnit(selected.unit)}. A dash means no numeric value was reported.`}
        />
        <div
          className="table-scroll"
          role="region"
          aria-label={`${selected.label} annual values by station and year`}
          tabIndex={0}
        >
          <table className="data-table">
            <caption className="sr-only">
              {selected.label} annual station summaries, {years[0]?.year ?? ""} to{" "}
              {years[years.length - 1]?.year ?? ""}
            </caption>
            <thead>
              <tr>
                <th scope="col">Station</th>
                {years.map((point) => (
                  <th
                    scope="col"
                    key={point.year}
                    className={point.year === latest?.year ? "is-latest" : ""}
                  >
                    {point.year}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {matrix.map((row) => (
                <tr key={row.name}>
                  <th scope="row">
                    <span>{row.name}</span>
                    <small>{row.zone || "Lake zone not reported"}</small>
                  </th>
                  {row.values.map((value, index) => (
                    <td
                      key={`${row.name}-${years[index]?.year ?? index}`}
                      className={
                        years[index]?.year === latest?.year ? "is-latest" : ""
                      }
                      title={
                        value === null
                          ? "No numeric value reported"
                          : `${row.name}, ${years[index]?.year}: ${formatWithUnit(
                              value,
                              selected.unit,
                            )}`
                      }
                    >
                      {value === null ? "—" : formatNumber(value)}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <WeatherSection />
      <AnalysisGallery />
    </>
  )
}

function auditDecisionLabel(decision: string): string {
  if (decision === "accepted_as_reported_event") {
    return "Accepted as reported event"
  }
  if (decision === "excluded_pending_verification") {
    return "Excluded pending verification"
  }
  return "Excluded"
}

function auditDecisionTone(
  decision: string,
): "positive" | "warning" | "danger" | "neutral" {
  if (decision === "accepted_as_reported_event") return "positive"
  if (decision === "excluded_pending_verification") return "warning"
  return "danger"
}

function EvidencePage() {
  return (
    <>
      <PageHeading
        index={PAGE_META.evidence.index}
        label={PAGE_META.evidence.label}
        title={PAGE_META.evidence.title}
        intro={PAGE_META.evidence.intro}
        actions={
          <a
            className="button button--secondary"
            href={event.sourceUrl}
            target="_blank"
            rel="noreferrer"
          >
            Open source article ↗
          </a>
        }
      />

      <Notice
        title="Reported event, not independently verified"
        action={
          <a className="text-link" href="#model">
            See the model limits →
          </a>
        }
      >
        <p>
          One UP Diliman article reports a fish kill in Biñan and Pila in May
          2019. No formal LLDA or BFAR incident report was supplied, and the
          report has not been independently corroborated in the available files.
        </p>
      </Notice>

      <section className="panel" aria-labelledby="event-record-title">
        <div className="panel-heading panel-heading--split">
          <div>
            <p className="section-kicker">Event record · {event.id}</p>
            <h2 id="event-record-title">May 2019 fish kill</h2>
          </div>
          <Badge tone="warning">Reported, not verified</Badge>
        </div>

        <EvidenceLadder />

        <dl className="fact-grid">
          <div>
            <dt>First reported start</dt>
            <dd>{formatDate(event.start)}</dd>
            <small>Pila was reported from 12 May 2019</small>
          </div>
          <div>
            <dt>Approximate end</dt>
            <dd>{formatDate(event.end)}</dd>
            <small>Described only as “until the end of May”</small>
          </div>
          <div>
            <dt>Location</dt>
            <dd>{event.location}</dd>
            <small>Municipality-level; Barangay Linga named for Pila</small>
          </div>
          <div>
            <dt>Species reported</dt>
            <dd>{event.species}</dd>
          </div>
          <div>
            <dt>Lake zone</dt>
            <dd className="muted-value">Not reported</dd>
          </div>
          <div>
            <dt>Economic loss</dt>
            <dd className="muted-value">Not reported</dd>
          </div>
        </dl>

        <div className="text-block">
          <h3>Reported cause</h3>
          <p>{event.cause}</p>
        </div>
        <div className="text-block">
          <h3>Reported losses</h3>
          <p>{event.losses}</p>
        </div>

        <div className="precision-note">
          <p>
            <strong>Date precision.</strong> {event.datePrecision}
          </p>
          <p>
            <strong>Location precision.</strong> {event.locationPrecision}
          </p>
        </div>

        <div className="verification-box">
          <h3>Verification status</h3>
          <p>{event.verification}</p>
          <p>{event.notes}</p>
        </div>

        <div className="source-citation">
          <div>
            <span>Source</span>
            <a href={event.sourceUrl} target="_blank" rel="noreferrer">
              {event.sourceTitle}
            </a>
            <small>
              UP Diliman · published {formatDate(event.publicationDate)}
            </small>
          </div>
        </div>
      </section>

      <div className="two-column two-column--equal">
        <section className="panel" aria-labelledby="supports-title">
          <PanelHeading
            id="supports-title"
            title="What the evidence supports"
            description="Limited claims that stay close to the source."
          />
          <ul className="plain-list plain-list--supported">
            <li>A fish kill was reported in Biñan and Pila in May 2019.</li>
            <li>Tilapia and bangus were reported among the affected fish.</li>
            <li>
              The article attributes the kill to a green tide and oxygen
              deficiency.
            </li>
            <li>The report is traceable to a named institutional source.</li>
          </ul>
        </section>

        <section className="panel" aria-labelledby="not-established-title">
          <PanelHeading
            id="not-established-title"
            title="What is not established"
            description="These gaps prevent verified-event or prediction claims."
          />
          <ul className="plain-list plain-list--unsupported">
            <li>Independent corroboration or a formal investigation.</li>
            <li>A complete fish-loss count or economic loss.</li>
            <li>A station or lake-zone assignment.</li>
            <li>Pre-event water-quality conditions.</li>
            <li>That unrelated non-reports were verified non-events.</li>
          </ul>
        </section>
      </div>

      <section className="panel" aria-labelledby="sample-context-title">
        <PanelHeading id="sample-context-title" title="During-event water sample" />
        <p className="panel-lead">
          The article reports one water sample collected on 29 May 2019, during
          or near the end of the event. It is retained as context only. It is
          never used as a pre-event predictor.
        </p>
      </section>

      <section className="panel" aria-labelledby="audit-title">
        <PanelHeading
          id="audit-title"
          title="Claim audit"
          description="Candidate claims reviewed before the event dataset was built."
        />
        <div className="audit-list">
          {data.evidenceAudit.map((record) => (
            <details className="audit-item" key={record.id}>
              <summary>
                <span className="audit-item__main">
                  <strong>{record.claim}</strong>
                  <small>
                    {record.id} · {record.source} · {record.locator}
                  </small>
                </span>
                <Badge tone={auditDecisionTone(record.decision)}>
                  {auditDecisionLabel(record.decision)}
                </Badge>
                <span className="details-mark" aria-hidden="true">
                  +
                </span>
              </summary>
              <div className="audit-item__body">
                <p>
                  <strong>Issue.</strong> {record.issue}
                </p>
                <p>
                  <strong>Decision.</strong> {record.reason}
                </p>
              </div>
            </details>
          ))}
        </div>
      </section>
    </>
  )
}

function SyntheticDemoPanel() {
  const metrics = syntheticDemo.metrics
  const training = syntheticDemo.training
  const detection = syntheticDemo.eventDetection
  const gapFill = syntheticDemo.gapFill

  return (
    <section className="panel" aria-labelledby="synthetic-demo-title">
      <PanelHeading
        id="synthetic-demo-title"
        title={syntheticDemo.title}
        description={syntheticDemo.summary}
        aside={<Badge tone="warning">{syntheticDemo.badge}</Badge>}
      />
      <div
        className="stats-grid stats-grid--three"
        aria-label="Synthetic gap-fill training metrics"
      >
        <StatCard
          value={formatNumber(metrics.f1, 3)}
          label="F1 score"
          note="72-hour synthetic test partition"
          tone="warning"
        />
        <StatCard
          value={formatNumber(metrics.prAuc, 3)}
          label="PR-AUC"
          note="Rare-event ranking quality"
          tone="warning"
        />
        <StatCard
          value={`${gapFill.readinessMet}/${gapFill.readinessTotal}`}
          label="Gap checks met"
          note="Synthetic training database"
          tone="warning"
        />
      </div>
      <p className="panel-lead">
        The model is <code>{syntheticDemo.modelPath}</code>, trained from{" "}
        <code>{syntheticDemo.databasePath}</code>. The database contains{" "}
        {formatNumber(gapFill.preEventObservations, 0)} dated pre-event rows,{" "}
        {formatNumber(gapFill.negativeWindows, 0)} non-event windows, and{" "}
        {gapFill.corroborationRecords} corroboration records.
      </p>
      <div className="two-column two-column--equal">
        <div>
          <h3 className="mini-heading">Test result</h3>
          <ul className="plain-list">
            <li>
              Precision: <strong>{formatNumber(metrics.precision, 3)}</strong>
            </li>
            <li>
              Recall: <strong>{formatNumber(metrics.recall, 3)}</strong>
            </li>
            <li>
              Brier score: <strong>{formatNumber(metrics.brier, 4)}</strong>
            </li>
            <li>
              Test rows: <strong>{formatNumber(metrics.testRows, 0)}</strong>
            </li>
            <li>
              Positive rows:{" "}
              <strong>{formatNumber(metrics.testPositives, 0)}</strong>
            </li>
            <li>
              Events detected:{" "}
              <strong>
                {detection.detected}/{detection.total}
              </strong>
            </li>
          </ul>
          <h3 className="mini-heading">Horizons</h3>
          <ul className="plain-list">
            {syntheticDemo.allMetrics.map((item) => (
              <li key={item.horizonHours}>
                {item.horizonHours}h F1{" "}
                <strong>{formatNumber(item.f1, 3)}</strong> · PR-AUC{" "}
                <strong>{formatNumber(item.prAuc, 3)}</strong>
              </li>
            ))}
          </ul>
        </div>
        <div>
          <h3 className="mini-heading">Gap-fill coverage</h3>
          <ul className="plain-list">
            <li>
              {gapFill.stationsWithCoordinates} station coordinates;{" "}
              {gapFill.zoneAssignments} zone assignments
            </li>
            <li>
              {gapFill.incidentReports} incident reports;{" "}
              {gapFill.stressPatrolReports} no-event patrol reports
            </li>
            <li>
              {formatNumber(gapFill.negativeWindows, 0)} credible non-event
              windows
            </li>
            <li>
              {gapFill.corroborationRecords} independent corroboration records
            </li>
            <li>{gapFill.aggregationRules} per-station aggregation rules</li>
            <li>
              {gapFill.readinessMet}/{gapFill.readinessTotal} synthetic checks
              pass
            </li>
          </ul>
          <h3 className="mini-heading">Training provenance</h3>
          <ul className="plain-list">
            <li>
              {training.realAnchors} real annual anchors;{" "}
              {training.imputedAnchors} imputed;{" "}
              {training.provisional2025Anchors} provisional 2025 anchors
            </li>
            <li>
              Annual calibration MAE:{" "}
              <strong>{formatNumber(training.calibrationMae, 6)}</strong>
            </li>
            <li>{training.split}</li>
          </ul>
        </div>
      </div>
      <p className="fine-print">
        Report: <code>{syntheticDemo.reportPath}</code>. Real-data gate:{" "}
        <strong>{syntheticDemo.realState.gate}</strong>, tracked separately.
      </p>
    </section>
  )
}

function ModelPage() {
  const passCount = data.governance.readiness.filter(
    (check) => check.status === "pass",
  ).length
  const partialCount = data.governance.readiness.filter(
    (check) => check.status === "partial",
  ).length
  const failCount = data.governance.readiness.filter(
    (check) => check.status === "fail",
  ).length
  const trainingFailures = data.governance.trainingChecks.filter(
    (check) => check.status === "fail",
  ).length
  const evaluationFailures = data.governance.evaluationChecks.filter(
    (check) => check.status === "fail",
  ).length

  return (
    <>
      <PageHeading
        index={PAGE_META.model.index}
        label={PAGE_META.model.label}
        title={PAGE_META.model.title}
        intro={PAGE_META.model.intro}
        actions={
          <a className="button button--secondary" href="#evidence">
            Review event evidence
          </a>
        }
      />

      <SyntheticDemoPanel />

      <section className="status-panel" aria-labelledby="real-model-boundary-title">
        <div className="status-panel__body">
          <Badge tone="warning">Real-data boundary</Badge>
          <h2 id="real-model-boundary-title">
            Real-data model remains unavailable
          </h2>
          <p>
            The supplied real evidence does not yet meet the training gate. The
            synthetic run above is a separate experiment; it does not change the
            real risk state.
          </p>
          <p className="fine-print">
            A descriptive annual trend estimate is available on the Water data
            page. The real-data guard checks are listed below.
          </p>
        </div>
      </section>

      <section className="stats-grid stats-grid--three" aria-label="Model blockers">
        <StatCard
          value={data.coverage.datedWaterQualityRows}
          label="Dated water-quality rows"
          note="LLDA values are annual station summaries"
          tone="warning"
        />
        <StatCard
          value={data.coverage.eventReports}
          label="Independent event period"
          note="A chronological model split needs more"
          tone="warning"
        />
        <StatCard
          value="0"
          label="Credible 24-hour negatives"
          note="No incident-reporting completeness record"
          tone="warning"
        />
      </section>

      <div className="two-column two-column--equal">
        <section className="panel" aria-labelledby="reasons-title">
          <PanelHeading
            id="reasons-title"
            title="Why real-data risk is unavailable"
            description="These blockers apply to the supplied evidence, not the synthetic run."
          />
          <ul className="plain-list plain-list--unsupported">
            {data.risk.reasons.map((reason) => (
              <li key={reason}>{reason}</li>
            ))}
          </ul>
        </section>

        <section className="panel" aria-labelledby="requirements-title">
          <PanelHeading
            id="requirements-title"
            title="What would change the real-data status"
            description="A defensible real-data model would need all of these."
          />
          <ol className="numbered-list">
            <li>Dated water-quality observations before each event.</li>
            <li>
              At least two independent event periods with exact dates for a
              chronological split.
            </li>
            <li>
              Documented incident reports that can support credible non-event
              windows.
            </li>
            <li>Station coordinates and an authoritative zone crosswalk.</li>
            <li>A documented per-station aggregation rule for annual values.</li>
            <li>Independent corroboration of event records.</li>
          </ol>
        </section>
      </div>

      <section className="panel" aria-labelledby="readiness-title">
        <PanelHeading
          id="readiness-title"
          title="Real-data model-readiness checks"
          description={`Real-data gate: ${passCount} of ${data.governance.readiness.length} checks fully met; ${partialCount} partial; ${failCount} not met.`}
        />
        <div
          className="readiness-meter"
          role="img"
          aria-label={`${passCount} of ${data.governance.readiness.length} model-readiness checks fully met`}
        >
          <span
            className="readiness-meter__fill"
            style={{
              width: `${Math.round(
                (passCount / data.governance.readiness.length) * 100,
              )}%`,
            }}
          />
        </div>
        <div className="readiness-legend" aria-hidden="true">
          <span>{passCount} fully met</span>
          <span>{partialCount} partial</span>
          <span>{failCount} not met</span>
        </div>
        <ol className="check-list">
          {data.governance.readiness.map((check) => (
            <li className="check-item" key={check.check}>
              <span className="check-id">{check.check}</span>
              <div className="check-copy">
                <h3>{check.requirement}</h3>
                <p>{check.evidence}</p>
                <p className="check-consequence">{check.consequence}</p>
              </div>
              <StatusBadge status={check.status} />
            </li>
          ))}
        </ol>
      </section>

      <div className="two-column two-column--equal">
        <section className="panel" aria-labelledby="guards-title">
          <PanelHeading
            id="guards-title"
            title="Real-data training guards"
            description="The real-data pipeline refuses to train or evaluate without valid labels. The synthetic run is separate and already trained."
          />
          <div className="guard-row">
            <div>
              <h3>Training guard</h3>
              <p>
                Refused before fitting a real-data fish-kill model.{" "}
                {trainingFailures} of{" "}
                {data.governance.trainingChecks.length} checks are not met, and
                the real fish-kill modelling dataset has zero data rows.
              </p>
            </div>
            <Badge tone="danger">Refused</Badge>
          </div>
          <div className="guard-row">
            <div>
              <h3>Evaluation guard</h3>
              <p>
                Refused because no fitted real-data fish-kill model or held-out
                predictions exist. {evaluationFailures} evaluation checks fail.
              </p>
            </div>
            <Badge tone="danger">Refused</Badge>
          </div>
          <p className="fine-print">
            Auditable status files: data/outputs/training_status.csv and
            data/outputs/evaluation_status.csv.
          </p>
        </section>

        <section className="panel" aria-labelledby="metrics-title">
          <PanelHeading
            id="metrics-title"
            title="Real-data fish-kill metrics are still absent"
          />
          <p className="panel-lead">
            Real-data fish-kill accuracy, precision, recall, F1, ROC-AUC,
            PR-AUC, and a confusion matrix are intentionally absent. The real
            evidence has no held-out prediction set from which to calculate
            them. The synthetic panel above reports its own trained-model
            metrics.
          </p>
          <p className="fine-print">
            The synthetic training panel above reports a separate exercise.
          </p>
        </section>
      </div>
    </>
  )
}

function SourcesPage() {
  return (
    <>
      <PageHeading
        index={PAGE_META.sources.index}
        label={PAGE_META.sources.label}
        title={PAGE_META.sources.title}
        intro={PAGE_META.sources.intro}
      />

      <section className="source-summary" aria-label="Source composition">
        <div>
          <strong>{data.sources.length}</strong>
          <span>supplied sources</span>
        </div>
        {["xlsx", "pdf", "docx", "zip", "md"].map((type) => {
          const count = sourceTypeCounts[type] ?? 0
          return (
            <div key={type}>
              <strong>{count}</strong>
              <span>
                {count === 1
                  ? SOURCE_TYPE_LABELS[type] ?? type
                  : SOURCE_TYPE_PLURALS[type] ?? type}
              </span>
            </div>
          )
        })}
      </section>

      <section className="panel" aria-labelledby="source-register-title">
        <PanelHeading
          id="source-register-title"
          title="Source register"
          description="Expand a source to see its period, contents, and use. File names are preserved as supplied."
        />
        <div className="source-list">
          {data.sources.map((source) => (
            <details className="source-item" key={source.id}>
              <summary>
                <span className="source-id">{source.id}</span>
                <span className="source-main">
                  <strong>{source.filename}</strong>
                  <small>
                    {SOURCE_TYPE_LABELS[source.type] ?? source.type} ·{" "}
                    {source.organization}
                  </small>
                </span>
                <span className="source-period">{source.period}</span>
                <span className="details-mark" aria-hidden="true">
                  +
                </span>
              </summary>
              <div className="source-body">
                <dl>
                  <div>
                    <dt>Publication</dt>
                    <dd>{source.publication}</dd>
                  </div>
                  <div>
                    <dt>Contents</dt>
                    <dd>{source.content}</dd>
                  </div>
                  <div>
                    <dt>Fish-kill records</dt>
                    <dd>{source.incidents}</dd>
                  </div>
                  <div>
                    <dt>Label suitability</dt>
                    <dd>{source.labels}</dd>
                  </div>
                  <div>
                    <dt>Use in HIMPIL</dt>
                    <dd>{source.used}</dd>
                  </div>
                </dl>
              </div>
            </details>
          ))}
        </div>
      </section>

      <div className="two-column two-column--equal">
        <section className="panel" aria-labelledby="quality-title">
          <PanelHeading
            id="quality-title"
            title="Data-quality notes"
            description="Rules applied across the processed data."
          />
          <ul className="quality-list">
            <li>
              <strong>Annual, not daily.</strong> Water-quality values are station
              year summaries. Weather values are monthly station summaries.
            </li>
            <li>
              <strong>Missing stays missing.</strong> Blank cells are not zeros
              and are never imputed.
            </li>
            <li>
              <strong>2025 weather is provisional.</strong> Seven stations have
              all 12 months; the rest have January–June values only. The source
              says the data are still undergoing verification.
            </li>
            <li>
              <strong>No coordinates.</strong> Only{" "}
              {data.coverage.lakeStationsWithZoneLabel} of{" "}
              {data.coverage.lakeStations} lake stations carry a zone label in
              their name. No authoritative crosswalk was supplied.
            </li>
            <li>
              <strong>No automatic name merge.</strong> “Angono” and “Angono
              River” remain separate because the files do not establish an
              equivalence.
            </li>
          </ul>
        </section>

        <section className="panel" aria-labelledby="provenance-title">
          <PanelHeading
            id="provenance-title"
            title="Provenance and limits"
            description="What was preserved and what remains unresolved."
          />
          <ul className="quality-list">
            <li>
              <strong>Original files unchanged.</strong> Source workbooks are
              copied and hash-checked; processed outputs are kept separate.
            </li>
            <li>
              <strong>One event period.</strong> The 2019 article is stored as
              one reported event to avoid double-counting Biñan and Pila.
            </li>
            <li>
              <strong>Aggregates were not expanded.</strong> The 1972–1998
              statement remains background evidence, not a set of invented
              events.
            </li>
            <li>
              <strong>Open issue.</strong> The DO workbook note says “2014 water
              quality data is only from January to June”; this likely refers to
              2024 and still needs LLDA confirmation.
            </li>
            <li>
              <strong>Build date.</strong> Dashboard bundle generated{" "}
              {formatDate(data.generatedAtUtc.slice(0, 10))}.
            </li>
          </ul>
        </section>
      </div>
    </>
  )
}

function App() {
  const [active, setActive] = useState<PageId>(() => readPageFromHash())

  useEffect(() => {
    const handleHashChange = () => setActive(readPageFromHash())
    window.addEventListener("hashchange", handleHashChange)
    return () => window.removeEventListener("hashchange", handleHashChange)
  }, [])

  useEffect(() => {
    document.title = `${PAGE_META[active].label} | HIMPIL`
    window.scrollTo({ top: 0, behavior: "auto" })
  }, [active])

  const page = (() => {
    if (active === "water") return <WaterPage />
    if (active === "evidence") return <EvidencePage />
    if (active === "model") return <ModelPage />
    if (active === "sources") return <SourcesPage />
    return <OverviewPage />
  })()

  return (
    <div className="app-shell">
      <a className="skip-link" href="#main">
        Skip to content
      </a>

      <div className="global-notice">
        <div className="page-width global-notice__inner">
          <span className="global-notice__dot" aria-hidden="true" />
          <span>
            <strong>Synthetic experiment.</strong> A 24/48/72-hour fish-kill
            model is trained on gap-filled data. Real monitoring values are
            annual or monthly summaries, not live readings.
          </span>
          <a href="#model">Model run</a>
        </div>
      </div>

      <header className="site-header">
        <div className="page-width header-inner">
          <a className="brand" href="#overview" aria-label="HIMPIL overview">
            <span className="brand-mark" aria-hidden="true">
              <svg viewBox="0 0 32 32">
                <path d="M5 17c4-6 8-6 11 0s7 6 11 0" />
                <path d="M5 23c4-6 8-6 11 0s7 6 11 0" />
              </svg>
            </span>
            <span className="brand-copy">
              <strong>HIMPIL</strong>
              <small>Laguna de Bay · Evidence dashboard</small>
            </span>
          </a>

          <nav className="primary-nav" aria-label="Primary navigation">
            {NAV_ITEMS.map((item) => (
              <a
                href={`#${item.id}`}
                key={item.id}
                aria-current={active === item.id ? "page" : undefined}
              >
                <span className="nav-index" aria-hidden="true">
                  {item.index}
                </span>
                <span>{item.label}</span>
              </a>
            ))}
          </nav>

          <a className="status-pill status-pill--synthetic" href="#model">
            <span aria-hidden="true" />
            Synthetic model trained
          </a>
        </div>
      </header>

      <main className="page-width app-main" id="main" tabIndex={-1}>
        {page}
      </main>

      <footer className="site-footer">
        <div className="page-width footer-inner">
          <div className="footer-brand">
            <strong>HIMPIL</strong>
            <p>
              Research prototype, not an official warning service. Water quality
              is annual; weather is monthly. Missing values remain missing.
            </p>
          </div>
          <div className="footer-meta">
            <span>{data.coverage.sourceCount} sources</span>
            <span>Build {formatDate(data.generatedAtUtc.slice(0, 10))}</span>
          </div>
          <a className="footer-top" href="#overview">
            Back to top ↑
          </a>
        </div>
      </footer>
    </div>
  )
}

export default App
