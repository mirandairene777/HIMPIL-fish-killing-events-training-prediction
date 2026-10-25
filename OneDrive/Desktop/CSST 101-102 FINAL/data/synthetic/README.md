# Synthetic data — simulation only

> **SIMULATION ONLY — NOT EVIDENCE**
>
> No daily value in this folder is a real measurement of Laguna de Bay. The base
> dataset uses real station labels and real annual anchors for calibration, but
> every daily value is generated. The prototype's dates, weather, events, labels,
> probabilities, and metrics are also generated. Nothing here is evidence or a
> real fish-kill record.

There are four separate synthetic artifacts in this folder. Do not confuse them.

## 1. Synthetic base dataset (primary)

`data/synthetic/base/` is the requested base dataset. It mirrors the real HIMPIL
station/year/variable frame:

- 15 real lake station labels from the supplied LLDA workbooks;
- 2016-01-01 through 2025-12-31;
- nitrate, phosphate, BOD, pH, water temperature, and dissolved oxygen;
- three synthetic weather zones calibrated to nearby PAGASA monthly summaries;
- real annual station-year anchors where available, with missing cells imputed
  and flagged;
- CSV files, a SQLite database, a data dictionary, and a manifest.

| File | Description |
|---|---|
| `base/stations.csv` | Real station labels and supplied zone metadata; no coordinates. |
| `base/calibration_anchors.csv` | Real annual anchors and synthetic imputation flags. |
| `base/water_quality_daily.csv` | Synthetic daily water-quality panel, wide format. |
| `base/weather_daily.csv` | Synthetic daily weather for three synthetic zones. |
| `base/himpil_synthetic_base.sqlite` | SQLite tables plus a long-format view and metadata. |
| `base/data_dictionary.md` | Column definitions, units, method, and limits. |
| `base/manifest.json` | Seed, source hashes, counts, calibration, quarantine flags. |

Regenerate it with:

```powershell
.\.venv\Scripts\python.exe sandbox\synthetic\build_base_dataset.py
```

See [`base/README.md`](base/README.md) and
[`../../reports/tables/synthetic_base_report.md`](../../reports/tables/synthetic_base_report.md).

## 2. Synthetic base model (secondary)

`data/synthetic/base_model/` is a **separate event-overlay exercise** built from
the base dataset. It injects 20 synthetic event periods and 10 high-stress
no-event periods into a copy of the daily panel, then trains 24/48/72-hour
models. The base dataset itself is unchanged.

| File | Description |
|---|---|
| `base_model/synthetic_events.csv` | Synthetic event and stress-only schedule. |
| `base_model/synthetic_modeling_dataset.csv` | Event-overlay panel, features, labels, split, and eligibility flags. |
| `base_model/synthetic_test_predictions.csv` | Held-out test probabilities and 24-hour alerts. |
| `base_model/manifest.json` | Seed, source hashes, metrics, and quarantine flags. |
| `base_model/README.md` | Data rules and file descriptions. |

Models are in `models/synthetic/base_model/`. Reports are in
`reports/tables/synthetic_base_model_*` and
[`../../reports/tables/system_gaps_and_todo.md`](../../reports/tables/system_gaps_and_todo.md).

Regenerate it with:

```powershell
.\.venv\Scripts\python.exe sandbox\synthetic\build_base_dataset.py
.\.venv\Scripts\python.exe sandbox\synthetic\train_base_model.py
```

The synthetic metrics are an artifact of the injected event process. They are
**not** real HIMPIL performance and do not satisfy the Section 6 gate.

## 3. Synthetic gap-filled database and model (training demo)

`data/synthetic/gap_fill/` fills the structural training checks in a synthetic
scope. It adds exact-dated events, 400 pre-event rows, 30 incident/patrol
reports, 1,700 monthly no-event windows, 40 corroboration records, 15 station
coordinates, a 15-station zone crosswalk, and 15 per-station aggregation rules.

| File | Description |
|---|---|
| `gap_fill/himpil_synthetic_complete.sqlite` | Main database with stations, water quality, weather, incidents, negative windows, readiness checks, modeling table, and pre-event audit table. |
| `gap_fill/stations.csv` | Synthetic coordinates and zone crosswalk. |
| `gap_fill/incident_reports.csv` | Synthetic event and no-event patrol reports. |
| `gap_fill/corroboration.csv` | Two independent synthetic sources per event. |
| `gap_fill/negative_windows.csv` | Monthly no-event windows with patrol coverage. |
| `gap_fill/aggregation_rules.csv` | Per-station annual aggregation rules. |
| `gap_fill/readiness_checks.csv` | Synthetic-scope checks plus the real-gate status. |
| `gap_fill/pre_event_observations.csv` | Dated water-quality rows before each event. |
| `gap_fill/manifest.json` | Counts, hashes, provenance, and quarantine metadata. |

Models are in `models/synthetic/gap_filled/`. Reports are
`reports/tables/synthetic_gap_fill_database_report.md` and
`reports/tables/synthetic_gap_filled_model_report.md`.

Regenerate with:

```powershell
.\.venv\Scripts\python.exe sandbox\synthetic\build_gap_filled_database.py
.\.venv\Scripts\python.exe sandbox\synthetic\train_gap_filled_model.py
```

The synthetic gate passes 10/10; the real gate remains 2 pass and 8 fail.

## 4. Generic model-prototype demo (secondary)

The files directly under `data/synthetic/` are the earlier generic demonstration:

| File | Description |
|---|---|
| `synthetic_station_day.csv` | Simulated station-day panel, six `SYN-LAG-*` stations, 2021-2024. |
| `synthetic_event_periods.csv` | Simulated event and high-stress no-event periods. |
| `synthetic_modeling_dataset.csv` | Feature matrix, 24/48/72-hour labels, and split. |
| `synthetic_test_predictions.csv` | Held-out simulated predictions. |
| `synthetic_manifest.json` | Seed, counts, split sizes, and quarantine status. |

This demo is **not** derived from the real station/year schema and is **not** the
base dataset. It exists only to exercise the modelling pipeline.

Regenerate it with:

```powershell
.\.venv\Scripts\python.exe sandbox\synthetic\run_prototype.py
```

## Rules

- Do not copy any synthetic file into `data/processed/`.
- Do not join synthetic daily values to real station measurements.
- Do not load synthetic data into the evidence dashboard.
- Do not replace `models/model.joblib` with a synthetic model.
- Do not treat missing/zero behavior as a real data-quality finding.
- Do not use simulated event dates as historical incidents.
- Do not claim the Section 6 model-readiness gate passed.

See [`../../sandbox/synthetic/README.md`](../../sandbox/synthetic/README.md),
[`../../reports/tables/synthetic_base_report.md`](../../reports/tables/synthetic_base_report.md),
[`../../reports/tables/synthetic_base_model_report.md`](../../reports/tables/synthetic_base_model_report.md),
[`../../reports/tables/synthetic_base_model_card.md`](../../reports/tables/synthetic_base_model_card.md),
[`../../reports/tables/system_gaps_and_todo.md`](../../reports/tables/system_gaps_and_todo.md),
and [`../../reports/tables/synthetic_model_card.md`](../../reports/tables/synthetic_model_card.md).
