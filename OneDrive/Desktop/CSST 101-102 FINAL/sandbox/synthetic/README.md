# HIMPIL synthetic sandbox

> **SIMULATION ONLY — NOT EVIDENCE**
>
> This folder produces synthetic data and a synthetic model demonstration. It is
> not a study of Laguna de Bay. The base dataset uses real station labels and
> annual anchors for calibration; its daily weather, measurements, and dates are
> generated. The generic prototype is entirely generated. Nothing here may be
> quoted as real HIMPIL performance or used for a real warning.

## Four separate synthetic artifacts

| Artifact | Script | Output | Purpose |
|---|---|---|---|
| **Synthetic base dataset** (primary) | `build_base_dataset.py` | `data/synthetic/base/` | Daily data on the real 15-station/2016-2025 frame, calibrated to real annual anchors. |
| **Synthetic base model** (secondary) | `train_base_model.py` | `data/synthetic/base_model/`, `models/synthetic/base_model/` | Event-overlay model on the base panel, for pipeline testing only. |
| **Synthetic gap-filled database and model** (training demo) | `build_gap_filled_database.py`, `train_gap_filled_model.py` | `data/synthetic/gap_fill/`, `models/synthetic/gap_filled/` | End-to-end database and 24/48/72-hour models with synthetic dates, incidents, negatives, coordinates, zones, aggregation rules, and corroboration. |
| **Generic model prototype** (secondary) | `run_prototype.py` | `data/synthetic/synthetic_*`, `models/synthetic/` | A toy 6-station/2021-2024 world for testing the modelling pipeline. |

The base dataset is **not** an input to the toy prototype. The toy prototype is
**not** the base dataset. The base model and gap-filled database are separate
synthetic exercises and do not modify the base dataset. Keep all four separate
from the real evidence track.

---

## Part A — Synthetic base dataset

### Why it exists

The supplied LLDA water quality is annual and the supplied PAGASA weather is
monthly. The team needs a daily working dataset to build and test joins, figures,
and software while real daily observations are pending. This base dataset fills
that software need without pretending the values are observations.

### What it contains

- **Stations:** the 15 real lake station labels from the supplied workbooks.
- **Calendar:** 2016-01-01 to 2025-12-31.
- **Water quality:** nitrate, phosphate, BOD, pH, water temperature, and dissolved
  oxygen, in the real units.
- **Weather:** rainfall, wind speed, and air temperature for three **synthetic**
  weather zones.
- **Anchors:** real annual station-year summaries where available. Missing annual
  cells are imputed from the station's other years or the lake-network mean and
  are explicitly flagged.
- **Formats:** CSV, SQLite, data dictionary, and manifest.

### Build

From the project root:

```powershell
.\.venv\Scripts\python.exe sandbox\synthetic\build_base_dataset.py
```

Deterministic seed: `20261023`. To use another seed:

```powershell
.\.venv\Scripts\python.exe sandbox\synthetic\build_base_dataset.py --seed 20261024
```

### Outputs

| Artifact | Path |
|---|---|
| Stations | `data/synthetic/base/stations.csv` |
| Calibration anchors | `data/synthetic/base/calibration_anchors.csv` |
| Daily water quality | `data/synthetic/base/water_quality_daily.csv` |
| Daily weather | `data/synthetic/base/weather_daily.csv` |
| SQLite database | `data/synthetic/base/himpil_synthetic_base.sqlite` |
| Data dictionary | `data/synthetic/base/data_dictionary.md` |
| Manifest | `data/synthetic/base/manifest.json` |
| Dataset README | `data/synthetic/base/README.md` |
| Calibration audit | `reports/tables/synthetic_base_calibration.csv` |
| Coverage table | `reports/tables/synthetic_base_coverage.csv` |
| Report | `reports/tables/synthetic_base_report.md` |

### Method and limits

1. Read the real annual lake station-year summaries.
2. For each station-year-variable with a real numeric value, generate a daily
   seasonal series and rescale it to the annual anchor.
3. For a missing annual cell, impute from the same station's available years, then
   from the lake-network mean, and record the imputation status.
4. Keep 2025 anchors but flag their completeness as unverified.
5. Generate weather independently for three synthetic zones. The monthly rainfall
   and wind targets come from real nearby PAGASA summaries; the zone mapping is a
   calibration device, not a real station-to-lake mapping.
6. Do **not** generate fish-kill labels, real event dates, coordinates, risk
   scores, or model metrics.

The daily series are intentionally complete. That is a software convenience, not
a claim that real monitoring is complete.

---

## Part B — Synthetic base model

### Why it exists

The base dataset has no fish-kill labels. To exercise the modelling pipeline
without touching the real evidence, `train_base_model.py` injects a **known
synthetic event process** into a copy of the base panel, builds 24/48/72-hour
labels, and trains chronological baselines.

### Build

```powershell
.\.venv\Scripts\python.exe sandbox\synthetic\build_base_dataset.py
.\.venv\Scripts\python.exe sandbox\synthetic\train_base_model.py
```

### What it contains

- 20 synthetic event periods and 10 high-stress no-event periods over 2016-2025.
- A four-day pre-event ramp, three-day event, and five-day recovery.
- 54,795 panel rows; 53,950 model-eligible rows.
- 15 real lake station labels; all daily values remain synthetic.
- Chronological split: train < 2023, validation = 2023, test = 2024-2025.
- Random forest, logistic regression, and majority-class baselines.
- Metrics, event detection, predictions, feature importance, a model card, and a
  manifest.

### Outputs

| Artifact | Path |
|---|---|
| Synthetic events | `data/synthetic/base_model/synthetic_events.csv` |
| Event-overlay panel | `data/synthetic/base_model/synthetic_modeling_dataset.csv` |
| Test predictions | `data/synthetic/base_model/synthetic_test_predictions.csv` |
| Manifest | `data/synthetic/base_model/manifest.json` |
| Models | `models/synthetic/base_model/*.joblib` |
| Report | `reports/tables/synthetic_base_model_report.md` |
| Model card | `reports/tables/synthetic_base_model_card.md` |
| Metrics | `reports/tables/synthetic_base_model_metrics.csv` |
| Diagnostics | `reports/tables/synthetic_base_model_diagnostics.csv` |
| Event detection | `reports/tables/synthetic_base_event_detection.csv` |
| Gaps and to-do | `reports/tables/system_gaps_and_todo.md` |

### Limits

The event effect is injected into the same variables used as features. The
metrics are therefore optimistic by construction. They are not evidence that
Laguna de Bay fish kills are predictable. The 24-hour model also shows a
label-timing problem: early alerts 2-3 days before an event are counted as false
positives. The test set has only four synthetic event periods.

### P6 experiment: lead-time policy (2026-10-23)

`lead_time_policy.py` is a read-only analysis of the saved 24-hour model. It
compares four confirmation/cooldown policies against a 72-hour lead window. The
recommended illustrative policy requires **two stations** to alert on the same
day and applies a **72-hour cooldown**. In the synthetic test split it issues
four episodes, detects all four events, and has zero false episodes; the first
alerts arrive two to three days before the synthetic event starts. The validation
split also detects both events with zero false episodes.

This is **post hoc**: the policies were chosen after the existing 24-hour error
profile was inspected. It is not a validated warning rule, not a new model, and
not evidence about Laguna de Bay. The raw station-day alert burden remains 44 in
the test split; confirmation reduces issued episodes, not the underlying errors.

Build:

```powershell
.\.venv\Scripts\python.exe sandbox\synthetic\lead_time_policy.py
```

Outputs:

| Artifact | Path |
|---|---|
| Policy comparison | `reports/tables/synthetic_lead_time_policy.csv` |
| Event-level lead times | `reports/tables/synthetic_lead_time_events.csv` |
| Report | `reports/tables/synthetic_lead_time_policy_report.md` |

### P7 presentation model: five inputs (2026-10-24)

`train_presentation_model.py` trains a small random forest on the synthetic
**72-hour** event label using only the five fields from the team's illustrative
training-data table: dissolved oxygen, water temperature, pH, rainfall, and wind
speed. It is a **presentation demo**, not a replacement for the full synthetic
base model.

In the synthetic test split it reports precision **0.4032**, recall **0.8333**,
F1 **0.5435**, and PR-AUC **0.6947**; it issues **124** station-day alerts
(**50** true positives, **74** false positives, **10** missed positives) and
detects **4/4** synthetic events. Validation reports F1 **0.7059** and detects
**2/2** events. The five-input model is simpler than the full 72-hour model
(F1 **0.797**), which is the point: it matches the team's proposed input table,
not the best synthetic result.

The model maps its simulated probability to an illustrative Low/Medium/High
band. Those bands are **communication labels, not validated thresholds**. The
six example rows from the team slide are fictional; they are included only to
show the interface. This model is simulation only, not evidence, and is not
connected to the evidence dashboard.

Build and run:

```powershell
.\.venv\Scripts\python.exe sandbox\synthetic\train_presentation_model.py
.\.venv\Scripts\python.exe sandbox\synthetic\predict_presentation.py --do 4.8 --temp 30 --ph 7.0 --rain 15 --wind 8
```

Outputs:

| Artifact | Path |
|---|---|
| Model | `models/synthetic/presentation/risk_demo_model.joblib` |
| Manifest | `models/synthetic/presentation/manifest.json` |
| Metrics | `reports/tables/synthetic_presentation_model_metrics.csv` |
| Feature importance | `reports/tables/synthetic_presentation_model_feature_importance.csv` |
| Example inputs | `reports/tables/synthetic_presentation_model_examples.csv` |
| Report | `reports/tables/synthetic_presentation_model_report.md` |

---

## Part B2 - Synthetic gap-filled database and model (2026-10-24)

The base model fills event labels but not the rest of the readiness structure.
`build_gap_filled_database.py` adds synthetic incident reports, no-event patrol
windows, station coordinates, a zone crosswalk, per-station aggregation rules,
and independent corroboration. `train_gap_filled_model.py` trains 24/48/72-hour
random forests from the database and publishes the dashboard payload.

```powershell
.\.venv\Scripts\python.exe sandbox\synthetic\build_gap_filled_database.py
.\.venv\Scripts\python.exe sandbox\synthetic\train_gap_filled_model.py
```

Outputs:

| Artifact | Path |
|---|---|
| Database | `data/synthetic/gap_fill/himpil_synthetic_complete.sqlite` |
| Audit CSVs | `data/synthetic/gap_fill/*.csv` |
| Models | `models/synthetic/gap_filled/` |
| Database report | `reports/tables/synthetic_gap_fill_database_report.md` |
| Model report | `reports/tables/synthetic_gap_filled_model_report.md` |
| Dashboard payload | `dashboard/src/data/syntheticDemo.json` |

The synthetic gate passes **10/10**; the real gate remains **2 pass, 8 fail**.
Test 72h: precision **0.670**, recall **0.983**, F1 **0.797**, PR-AUC **0.939**,
Brier **0.0029**, and **4/4** events detected.

## Part C - Generic model prototype

### Why it exists

The real project is blocked by evidence, not by software. The team still needs a
runnable prototype to test a chronological modelling pipeline and explain the
intended workflow. This part generates a **known** synthetic world, trains
baseline models, evaluates them chronologically, and produces a model card.

### Quick start

```powershell
.\.venv\Scripts\python.exe sandbox\synthetic\run_prototype.py
```

The script is deterministic by default (seed `20261023`). To run a different
simulation:

```powershell
.\.venv\Scripts\python.exe sandbox\synthetic\run_prototype.py --seed 20261024
```

### What is generated

| Artifact | Path | Purpose |
|---|---|---|
| Synthetic station-day panel | `data/synthetic/synthetic_station_day.csv` | Simulated weather and water quality |
| Event truth table | `data/synthetic/synthetic_event_periods.csv` | Simulated event and stress periods |
| Modelling table | `data/synthetic/synthetic_modeling_dataset.csv` | Features, labels, split, eligibility |
| Test predictions | `data/synthetic/synthetic_test_predictions.csv` | Held-out simulated predictions |
| Manifest | `data/synthetic/synthetic_manifest.json` | Seed, counts, quarantine status |
| Models | `models/synthetic/*.joblib` | Random forest, logistic, and dummy artifacts |
| Report | `reports/tables/synthetic_prototype_report.md` | Full simulation report |
| Model card | `reports/tables/synthetic_model_card.md` | Intended use and prohibited use |
| Metrics | `reports/tables/synthetic_prototype_metrics.csv` | All metrics and confusion counts |
| Feature importance | `reports/tables/synthetic_feature_importance.csv` | Simulation-only ranking |
| Event detection | `reports/tables/synthetic_event_detection.csv` | Event-level test check |

### Design

- **Calendar:** 2021-01-01 to 2024-12-31. Synthetic dates only.
- **Stations:** `SYN-LAG-01` to `SYN-LAG-06`, in `SYN-ZONE-A` to `SYN-ZONE-C`.
- **Weather:** seasonal rainfall, wind, and air temperature.
- **Water quality:** DO, water temperature, pH, nitrate, phosphate, and BOD.
- **Events:** eight simulated event periods across four years. Each event affects
  two or three synthetic stations.
- **Stress-only periods:** three high-stress periods with no event label, included
  to make false-positive analysis meaningful.
- **Features:** current conditions plus backward-looking lags and rolling means.
  Event and recovery rows are excluded from fitting and evaluation.
- **Targets:** event start within 24, 48, or 72 hours at the same station.
- **Split:** chronological train (2021-2022), validation (2023), and test (2024).
- **Models:** majority-class baseline, logistic regression, and random forest.

### Quarantine rules

1. Do not copy synthetic rows into `data/processed/`.
2. Do not replace `models/model.joblib` with a synthetic artifact.
3. Do not load synthetic data or metrics into `dashboard/src/data/dashboard.json`.
4. Do not describe the synthetic model as the HIMPIL model without “synthetic
   prototype” and “simulation only.”
5. Do not use a synthetic probability to issue an advisory.
6. Do not claim the Section 6 gate passed because either script runs.

The real dashboard must continue to say **risk assessment unavailable**. The real
guards must continue to refuse.

### What the prototype proves

- The pipeline can build a daily panel and leakage-aware features.
- The pipeline can make chronological train/validation/test splits.
- The code can evaluate rare-event metrics and event-level detection.
- The team can review a model card and a reproducible report.
- The outputs can be quarantined cleanly.

### What it does not prove

- That Laguna de Bay fish kills are predictable.
- That any real station or zone has a risk level.
- That the synthetic feature importances are ecological findings.
- That the synthetic precision, recall, F1, or PR-AUC will transfer to real data.
- That the original operational goal has been met.
- That the synthetic base dataset is evidence.

### Suggested use

Use the prototype for:

- onboarding a teammate to the modelling code;
- testing a future dashboard layout on a separate branch;
- practicing a defense explanation of why the real model is blocked;
- reviewing label definitions, leakage controls, and metric reporting.

Do not use it for:

- a public demo that implies a live Laguna de Bay warning;
- a thesis result or abstract;
- a data-request claim;
- an advisory or SMS prototype with real beneficiaries.

## Related documents

- [`README.md`](../../README.md) — full team guide.
- [`README_WORKPLAN.md`](../../README_WORKPLAN.md) — living source of truth.
- [`data/synthetic/base/README.md`](../../data/synthetic/base/README.md) — synthetic base dataset.
- [`data/synthetic/base/data_dictionary.md`](../../data/synthetic/base/data_dictionary.md) — base schema and method.
- [`reports/tables/synthetic_base_report.md`](../../reports/tables/synthetic_base_report.md) — base dataset report.
- [`data/synthetic/base_model/README.md`](../../data/synthetic/base_model/README.md) — base-model data rules.
- [`reports/tables/synthetic_base_model_report.md`](../../reports/tables/synthetic_base_model_report.md) — base-model report.
- [`reports/tables/synthetic_base_model_card.md`](../../reports/tables/synthetic_base_model_card.md) — base-model card.
- [`reports/tables/system_gaps_and_todo.md`](../../reports/tables/system_gaps_and_todo.md) — system gaps and to-do list.
- [`data/synthetic/README.md`](../../data/synthetic/README.md) — synthetic folder rules.
- [`reports/tables/synthetic_prototype_report.md`](../../reports/tables/synthetic_prototype_report.md) — model demo report.
- [`reports/tables/synthetic_model_card.md`](../../reports/tables/synthetic_model_card.md) — model demo card.
- [`models/synthetic/README.md`](../../models/synthetic/README.md) — synthetic model artifacts.
