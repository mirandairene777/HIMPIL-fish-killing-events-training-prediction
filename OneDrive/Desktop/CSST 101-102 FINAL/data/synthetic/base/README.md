# HIMPIL synthetic base dataset

> **SIMULATION ONLY - NOT EVIDENCE**
>
> This is a synthetic base dataset built from the project's real station labels,
> years, variables, units, and annual anchors. The daily values are generated.
> The annual anchors are real source values included only for calibration and
> audit. No daily value is a measurement of Laguna de Bay. Nothing here is a real
> fish-kill record or can support a real risk assessment.

## What this is

A quarantined, reproducible daily base dataset for software and workflow testing:

- 15 lake station labels from the supplied LLDA workbooks;
- 2016-01-01 through 2025-12-31;
- six water-quality variables: nitrate, phosphate, BOD, pH, water temperature, DO;
- three synthetic weather zones with rainfall, wind, and air temperature;
- real annual station-year anchors where available, with missing cells imputed and flagged.

## What this is not

- It is not evidence about Laguna de Bay.
- It is not the real HIMPIL model dataset.
- It does not contain fish-kill labels or real event dates.
- It does not satisfy the Section 6 model-readiness gate.
- It must not be connected to the evidence dashboard.

The real dashboard must continue to report **risk assessment unavailable**.

## Files

| File | Description |
|---|---|
| `stations.csv` | Real station labels and supplied zone metadata; no coordinates. |
| `calibration_anchors.csv` | Annual anchors and imputation flags used by the generator. |
| `water_quality_daily.csv` | Synthetic daily water-quality panel, wide format. |
| `weather_daily.csv` | Synthetic daily weather for three synthetic zones. |
| `himpil_synthetic_base.sqlite` | SQLite database with tables, a long-format view, and metadata. |
| `data_dictionary.md` | Column definitions, units, calibration method, and limits. |
| `manifest.json` | Seed, source hashes, counts, calibration summary, and quarantine flags. |

## Quick query

The SQLite file has a wide table and a long-format view:

```sql
SELECT station_name, date, do_mg_l
  FROM water_quality_daily
 WHERE station_id = 'LAG-LAKE-01'
 ORDER BY date
 LIMIT 10;

SELECT *
  FROM water_quality_daily_long
 LIMIT 10;
```

## Regeneration

```powershell
.\.venv\Scripts\python.exe sandbox\synthetic\build_base_dataset.py
```

The generator is deterministic by default (seed `20261023`). It reads the
real processed inputs but writes only to this folder and to the synthetic-base
report files under `reports/tables/`.

## Quarantine rules

1. Do not copy these files into `data/processed/`.
2. Do not replace `models/model.joblib` with a model trained on these data.
3. Do not load these values into `dashboard/src/data/dashboard.json`.
4. Do not describe a synthetic value as a Laguna de Bay measurement.
5. Do not use this dataset to issue an advisory.
6. Do not claim the real model gate passed.

See [`../../../sandbox/synthetic/README.md`](../../../sandbox/synthetic/README.md)
and [`../../../reports/tables/synthetic_base_report.md`](../../../reports/tables/synthetic_base_report.md).
