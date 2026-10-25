# HIMPIL synthetic prototype report

> **SIMULATION ONLY — NOT EVIDENCE**
>
> Every row, station, date, event, probability, and metric in this report comes
> from a synthetic data generator. This is **not** a study of Laguna de Bay, not
> a real fish-kill record, not a real risk assessment, and not a substitute for
> the Section 6 model-readiness gate. The real-data dashboard continues to show
> **risk assessment unavailable**.

**Generated (UTC):** 2026-10-23T09:36:51+00:00  
**Random seed:** `20261023`  
**Code:** [`sandbox/synthetic/run_prototype.py`](../../sandbox/synthetic/run_prototype.py)  
**Model card:** [`synthetic_model_card.md`](synthetic_model_card.md)  
**Guardrail:** this prototype is quarantined outside `data/processed/`, `models/model.joblib`, and the evidence dashboard.

## 1. What this prototype demonstrates

The prototype exercises the full workflow that the real study will need:

1. generate a daily station-day panel with weather and water-quality variables;
2. inject **known** simulated event periods and high-stress non-event periods;
3. build only backward-looking features and a 24/48/72-hour target;
4. split chronologically by date;
5. fit a majority-class baseline, a logistic regression, and a random forest;
6. evaluate precision, recall, F1, PR-AUC, ROC-AUC, Brier score, and a confusion matrix;
7. produce a model artifact, a model card, and an auditable report.

## 2. What it does not demonstrate

- It does **not** estimate real fish-kill risk in Laguna de Bay.
- It does **not** use real station coordinates, zones, event dates, or observations.
- It does **not** pass the Section 6 gate. The gate requires real daily observations,
  multiple verified event periods across years, credible negatives, station/zone
  mapping, a data dictionary, and leakage review.
- It does **not** justify a live warning, advisory, SMS alert, or public risk category.
- Its high or low metrics are properties of the simulation. They must never be
  quoted as HIMPIL's real-world performance.

## 3. Simulated data-generating process

- **Calendar:** 2021-01-01 to 2024-12-31; synthetic dates only.
- **Stations:** six synthetic stations (`SYN-LAG-01` to `SYN-LAG-06`) in three
  synthetic zones (`SYN-ZONE-A`, `SYN-ZONE-B`, `SYN-ZONE-C`).
- **Weather:** seasonal rainfall, wind, and air temperature with noise.
- **Water quality:** dissolved oxygen, water temperature, pH, nitrate, phosphate,
  and BOD. The baseline includes seasonal and station-level variation.
- **Event effect:** for affected stations, DO falls and temperature, nutrients,
  BOD, and pH shift over a four-day pre-event ramp, a three-day event, and a
  five-day recovery. Event labels are generated from the known simulation
  schedule.
- **Stress-only periods:** high-stress conditions with no event label. They create
  plausible false-positive windows and make the demonstration less trivial.
- **Data-origin column:** every row is marked `synthetic_simulation`.

### Simulated event periods

| ID | Start | End | Affected synthetic stations |
|---|---|---|---|
| SYN-EVT-2021-01 | 2021-04-19 | 2021-04-21 | SYN-LAG-01, SYN-LAG-02, SYN-LAG-03 |
| SYN-EVT-2021-02 | 2021-06-07 | 2021-06-09 | SYN-LAG-02, SYN-LAG-04 |
| SYN-EVT-2022-01 | 2022-05-09 | 2022-05-11 | SYN-LAG-01, SYN-LAG-03, SYN-LAG-05 |
| SYN-EVT-2022-02 | 2022-06-20 | 2022-06-22 | SYN-LAG-04, SYN-LAG-06 |
| SYN-EVT-2023-01 | 2023-04-17 | 2023-04-19 | SYN-LAG-02, SYN-LAG-03, SYN-LAG-06 |
| SYN-EVT-2023-02 | 2023-06-05 | 2023-06-07 | SYN-LAG-01, SYN-LAG-05 |
| SYN-EVT-2024-01 | 2024-05-13 | 2024-05-15 | SYN-LAG-01, SYN-LAG-04, SYN-LAG-06 |
| SYN-EVT-2024-02 | 2024-06-24 | 2024-06-26 | SYN-LAG-02, SYN-LAG-03, SYN-LAG-05 |

### Simulated high-stress, no-event periods

| ID | Start | End | Affected synthetic stations |
|---|---|---|---|
| SYN-STRESS-2022-01 | 2022-04-25 | 2022-04-27 | SYN-LAG-02, SYN-LAG-05 |
| SYN-STRESS-2023-01 | 2023-05-22 | 2023-05-24 | SYN-LAG-01, SYN-LAG-04 |
| SYN-STRESS-2024-01 | 2024-04-29 | 2024-05-01 | SYN-LAG-02, SYN-LAG-05 |

## 4. Target and split

For a row at date `t`:

- `y_24h = 1` when a simulated event starts the next day at that station.
- `y_48h = 1` when a simulated event starts within the next two days.
- `y_72h = 1` when a simulated event starts within the next three days.

Rows during an event and during the five-day recovery window are excluded from
model fitting and evaluation. Rows in stress-only periods remain eligible, so
false alarms are visible.

### Chronological partitions

| Split | Start | End | Rows | Event periods present |
|---|---|---|---:|---:|
| Train | 2021-01-01 | 2022-12-31 | 4380 | 4 |
| Validation | 2023-01-01 | 2023-12-31 | 2190 | 2 |
| Test | 2024-01-01 | 2024-12-31 | 2196 | 2 |

The split is by date, never random. A random split would leak the same simulated
event period into training and test.

## 5. Results (simulation only)

### Test partition — all models

| Model | Horizon (h) | Positives | Negatives | Precision | Recall | F1 | PR-AUC | ROC-AUC | Brier | TP | FP | FN | TN |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| dummy_prior | 24 | 6 | 2142 | 0.000 | 0.000 | 0.000 | 0.003 | 0.500 | 0.003 | 0 | 0 | 6 | 2142 |
| logistic_regression | 24 | 6 | 2142 | 0.545 | 1.000 | 0.706 | 0.915 | 1.000 | 0.002 | 6 | 5 | 0 | 2137 |
| random_forest | 24 | 6 | 2142 | 0.600 | 1.000 | 0.750 | 0.948 | 1.000 | 0.001 | 6 | 4 | 0 | 2138 |
| random_forest | 48 | 12 | 2136 | 0.800 | 1.000 | 0.889 | 1.000 | 1.000 | 0.001 | 12 | 3 | 0 | 2133 |
| random_forest | 72 | 18 | 2130 | 0.773 | 0.944 | 0.850 | 0.942 | 0.999 | 0.002 | 17 | 5 | 1 | 2125 |

### Validation partition — random forest

| Model | Horizon (h) | Positives | Negatives | Precision | Recall | F1 | PR-AUC | ROC-AUC | Brier | TP | FP | FN | TN |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| random_forest | 24 | 5 | 2145 | 0.800 | 0.800 | 0.800 | 0.925 | 1.000 | 0.001 | 4 | 1 | 1 | 2144 |
| random_forest | 48 | 10 | 2140 | 0.643 | 0.900 | 0.750 | 0.885 | 0.999 | 0.002 | 9 | 5 | 1 | 2135 |
| random_forest | 72 | 15 | 2135 | 0.591 | 0.867 | 0.703 | 0.762 | 0.960 | 0.004 | 13 | 9 | 2 | 2126 |

The test partition contains only two simulated event periods. The positive counts
are small, so the metrics are unstable even within the simulation. This is one
reason the numbers cannot be transferred to the real setting.

### Event-level test detection at threshold 0.50

| Event | Pre-event station rows | Alerts at 0.50 | Detected at least once | Max probability |
|---|---:|---:|---:|---:|
| SYN-EVT-2024-01 | 3 | 3 | yes | 0.916 |
| SYN-EVT-2024-02 | 3 | 3 | yes | 0.999 |

A missed event means every pre-event station row in that period stayed below
0.50. A detected event means at least one row crossed the threshold. This is a
demonstration of the evaluation code, not evidence of real warning skill.

## 6. Top random-forest features (simulation only)

| Rank | Feature | Importance (simulation) |
|---:|---|---:|
| 1 | `do_min3` | 0.1666 |
| 2 | `do_roll3_mean` | 0.1497 |
| 3 | `do_mg_l` | 0.1354 |
| 4 | `do_lag1` | 0.1193 |
| 5 | `bod_mg_l` | 0.1104 |
| 6 | `do_lag2` | 0.0952 |
| 7 | `nutrient_roll3_mean` | 0.0853 |
| 8 | `nitrate_mg_l` | 0.0356 |
| 9 | `phosphate_mg_l` | 0.0315 |
| 10 | `do_roll7_mean` | 0.0242 |

Feature importance is model-specific, unstable, and computed on synthetic data.
It must not be presented as a finding about Laguna de Bay.

## 7. Reproducibility and outputs

Run:

```powershell
.\.venv\Scripts\python.exe sandbox\synthetic\run_prototype.py
```

Outputs:

| Output | Path | Status |
|---|---|---|
| Synthetic panel | `data/synthetic/synthetic_station_day.csv` | simulation only |
| Event truth table | `data/synthetic/synthetic_event_periods.csv` | simulation only |
| Modelling table | `data/synthetic/synthetic_modeling_dataset.csv` | simulation only |
| Test predictions | `data/synthetic/synthetic_test_predictions.csv` | simulation only |
| Manifest | `data/synthetic/synthetic_manifest.json` | simulation only |
| Models | `models/synthetic/*.joblib` | quarantined |
| Metrics | `reports/tables/synthetic_prototype_metrics.csv` | simulation only |
| Feature importance | `reports/tables/synthetic_feature_importance.csv` | simulation only |
| Event detection | `reports/tables/synthetic_event_detection.csv` | simulation only |

## 8. Quarantine rules

1. Never copy these rows into `data/processed/` or the real dashboard.
2. Never call the synthetic model “the HIMPIL model” without “synthetic prototype”.
3. Never quote these metrics in a defense, abstract, or paper as real performance.
4. Never use this model to issue an advisory or risk level.
5. Remove or archive the prototype when real data and a real model replace it.

## 9. What the team should take from this

The prototype proves that the **software pipeline** can generate a panel, build
leakage-aware features, train models, evaluate rare-event metrics, and produce a
model card. It does not reduce the evidence gap. The next real milestone is still
data access: LLDA daily observations, station metadata, incident records,
reporting completeness, and an authoritative zone crosswalk.

See [`README_WORKPLAN.md`](../../README_WORKPLAN.md) Section 6 for the real gate.
