# Synthetic base dataset report

> **SIMULATION ONLY - NOT EVIDENCE**

This report describes a synthetic base dataset. It is **not** evidence about
Laguna de Bay and does **not** pass the Section 6 gate. The real dashboard must
continue to show **risk assessment unavailable**.

## Coverage

- Lake stations: **15** (exact labels from the supplied workbooks).
- Calendar: **2016-01-01 to 2025-12-31** (synthetic daily dates).
- Water-quality rows: **54,795** station-days.
- Water-quality variables: **6**.
- Weather rows: **10,959** across **3** synthetic zones.
- Annual anchors: **900** station-year-variable rows.
  - Real numeric anchors: **711**.
  - Synthetic imputed anchors: **189**.
  - 2025 anchors with unverified completeness: **90**.

## Calibration

The daily series are calibrated to the annual anchors. Realized annual means are
reported in `synthetic_base_calibration.csv`.

- Mean absolute annual-mean error: **0.000047**.
- Maximum absolute annual-mean error: **0.000464**.

Exact equality is not guaranteed because values are clipped to plausible
variable bounds and rounded to the displayed precision.

## Stations

| Station ID | Real station label | Supplied zone |
|---|---|---|
| `LAG-LAKE-01` | Stn I - West Bay | West Bay |
| `LAG-LAKE-02` | Stn II - East Bay | East Bay |
| `LAG-LAKE-03` | Stn IV - Central Bay | Central Bay |
| `LAG-LAKE-04` | Stn V - West Bay near Pasig River | West Bay |
| `LAG-LAKE-05` | Stn VIII - South Bay | South Bay |
| `LAG-LAKE-06` | Stn XV - San Pedro | (blank) |
| `LAG-LAKE-07` | Stn XVI -Sta. Rosa | (blank) |
| `LAG-LAKE-08` | Stn XVII - Sanctuary | (blank) |
| `LAG-LAKE-09` | Stn XVIII - Pagsanjan | (blank) |
| `LAG-LAKE-10` | Stn. XIII (Taytay) | (blank) |
| `LAG-LAKE-11` | Stn. XIX (Muntinlupa) | (blank) |
| `LAG-LAKE-12` | Stn. XX (GEMS) | (blank) |
| `LAG-LAKE-13` | Stn. XXI (Cardona) | (blank) |
| `LAG-LAKE-14` | Stn. XXII (Jala-jala) | (blank) |
| `LAG-LAKE-15` | Stn. XXIII (Lumban) | (blank) |

## Weather zones

These are synthetic zones. The calibration station is a real PAGASA summary used
only to shape monthly rainfall and wind; no real station-to-lake mapping is
claimed.

| Synthetic weather zone | Calibration source |
|---|---|
| `SYN-WX-WEST` | `Ambulong, Batangas` |
| `SYN-WX-CENTRAL` | `Tanay, Rizal` |
| `SYN-WX-EAST` | `Tayabas, Quezon` |

## Missingness and imputation

- Ten of the fifteen lake stations have no zone label in the source; their zone
  remains blank.
- The real annual water-temperature cell is missing for **39 station-years**,
  including all 15 in 2017; synthetic values are imputed and flagged.
- 2025 source values exist but their completeness is not documented; they are
  retained with an explicit flag.
- Synthetic daily values are complete by design. This is a convenience for
  software testing, not a claim that real monitoring is complete.

## What is absent

- No fish-kill labels.
- No real or synthetic event dates tied to a real incident.
- No station coordinates.
- No tributary stations; only the 15 lake stations are generated.
- No model training, metrics, risk scores, or advisories.
- No connection to `data/processed/` or the evidence dashboard.

## Files

- `data/synthetic/base/` — CSV, SQLite, data dictionary, manifest, README.
- `reports/tables/synthetic_base_calibration.csv` — annual calibration audit.
- `reports/tables/synthetic_base_coverage.csv` — synthetic ranges by year/variable.
- `reports/tables/synthetic_base_report.md` — this report.
