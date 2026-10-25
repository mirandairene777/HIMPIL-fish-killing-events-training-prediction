# Synthetic base model report

> **SIMULATION ONLY - NOT EVIDENCE**
>
> This is a model trained on a **synthetic event overlay** applied to the
> synthetic base dataset. It is not a study of Laguna de Bay, not a real
> fish-kill model, and not a real risk assessment. The base dataset is unchanged;
> the event effects and labels exist only in this separate exercise.

**Generated (UTC):** 2026-10-24T13:41:59+00:00  
**Code:** `sandbox/synthetic/train_base_model.py`  
**Seed:** `20261023`  
**Model card:** `reports/tables/synthetic_base_model_card.md`  
**Metrics:** `reports/tables/synthetic_base_model_metrics.csv`

## 1. What was trained

- **Input:** `data/synthetic/base/water_quality_daily.csv` and `weather_daily.csv`.
- **Station labels:** 15 real lake station labels from the supplied LLDA workbooks.
- **Calendar:** 2016-01-01 to 2025-12-31; all daily values are synthetic.
- **Event overlay:** 20 synthetic event periods and 10
  stress-only/no-event periods. Event dates are generated, not historical.
- **Event effect:** a four-day pre-event ramp, a three-day event, and a five-day
  recovery. Affected stations receive lower DO, higher temperature, higher
  nutrients, higher BOD, and slightly lower pH.
- **Targets:** event start within 24, 48, or 72 hours at the same station.
- **Features:** current conditions, backward-looking lags, rolling means, and
  rolling rainfall/wind/nutrient summaries. No future values are used.
- **Split:** chronological. Train < 2023-01-01, validation = 2023, test >= 2024-01-01.
- **Models:** majority-class baseline, logistic regression, and random forest.

## 2. Data and split counts

| Partition | All rows | Model-eligible rows | Positive 24h | Positive 48h | Positive 72h |
|---|---:|---:|---:|---:|---:|
| train | 38,355 | 37,750 | 70 | 140 | 210 |
| validation | 5,475 | 5,395 | 10 | 20 | 30 |
| test | 10,965 | 10,805 | 20 | 40 | 60 |
| all eligible | 53,950 | 53,950 | 100 | 200 | 300 |

Rows during an event and the five-day recovery window are excluded from fitting
and evaluation. Stress-only periods remain eligible, so false alarms are visible.

## 3. Test results (simulation only)

### Random forest

| Model | Horizon (h) | Pos | Neg | Precision | Recall | F1 | PR-AUC | ROC-AUC | Brier | TP | FP | FN | TN |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| random_forest | 24 | 20 | 10785 | 0.455 | 1.000 | 0.625 | 0.568 | 0.999 | 0.0020 | 20 | 24 | 0 | 10761 |
| random_forest | 48 | 40 | 10765 | 0.597 | 1.000 | 0.748 | 0.957 | 1.000 | 0.0021 | 40 | 27 | 0 | 10738 |
| random_forest | 72 | 60 | 10745 | 0.670 | 0.983 | 0.797 | 0.947 | 1.000 | 0.0026 | 59 | 29 | 1 | 10716 |

### All test models

| Model | Horizon (h) | Pos | Neg | Precision | Recall | F1 | PR-AUC | ROC-AUC | Brier | TP | FP | FN | TN |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| dummy_prior | 24 | 20 | 10785 | 0.000 | 0.000 | 0.000 | 0.002 | 0.500 | 0.0018 | 0 | 0 | 20 | 10785 |
| logistic_regression | 24 | 20 | 10785 | 0.513 | 1.000 | 0.678 | 0.923 | 1.000 | 0.0016 | 20 | 19 | 0 | 10766 |
| random_forest | 24 | 20 | 10785 | 0.455 | 1.000 | 0.625 | 0.568 | 0.999 | 0.0020 | 20 | 24 | 0 | 10761 |
| random_forest | 48 | 40 | 10765 | 0.597 | 1.000 | 0.748 | 0.957 | 1.000 | 0.0021 | 40 | 27 | 0 | 10738 |
| random_forest | 72 | 60 | 10745 | 0.670 | 0.983 | 0.797 | 0.947 | 1.000 | 0.0026 | 59 | 29 | 1 | 10716 |

### Validation — random forest

| Model | Horizon (h) | Pos | Neg | Precision | Recall | F1 | PR-AUC | ROC-AUC | Brier | TP | FP | FN | TN |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| random_forest | 24 | 10 | 5385 | 0.714 | 1.000 | 0.833 | 1.000 | 1.000 | 0.0005 | 10 | 4 | 0 | 5381 |
| random_forest | 48 | 20 | 5375 | 0.800 | 1.000 | 0.889 | 0.972 | 1.000 | 0.0008 | 20 | 5 | 0 | 5370 |
| random_forest | 72 | 30 | 5365 | 0.853 | 0.967 | 0.906 | 0.987 | 1.000 | 0.0010 | 29 | 5 | 1 | 5360 |

The test partition contains **4 synthetic event periods**. That is
too few for a defensible real-world evaluation. The scores are an artifact of
injecting a strong event signature into the same variables the model sees; they
are not evidence that real fish kills are predictable.

### 24-hour error profile by period type

| Period type | Rows | Positives | Alerts | TP | FP | FN | Max probability |
|---|---:|---:|---:|---:|---:|---:|---:|
| baseline | 10,653 | 0 | 0 | 0 | 0 | 0 | 0.409 |
| pre_event | 80 | 20 | 43 | 20 | 23 | 0 | 0.999 |
| stress_only | 72 | 0 | 1 | 0 | 1 | 0 | 0.564 |

The 24-hour false positives are mostly **pre-event rows 2–3 days before a
synthetic event**, not random baseline rows. The 24-hour target counts those
early warnings as false positives because the event is not within the next 24
hours. This is a **label-timing problem** for any future real model: a single
24-hour label does not credit an early warning that arrives too soon. The real
evaluation must use a lead-time policy that matches the intended advisory.

## 4. Event-level detection (24-hour model, test)

| Event | Start | Prediction rows | Alerts | Alerted any | Max probability |
|---|---|---:|---:|---:|---:|
| SYN-BASE-EVT-2024-01 | 2024-03-15 | 5 | 5 | 1 | 0.999 |
| SYN-BASE-EVT-2024-02 | 2024-06-16 | 5 | 5 | 1 | 0.629 |
| SYN-BASE-EVT-2025-01 | 2025-03-18 | 5 | 5 | 1 | 0.995 |
| SYN-BASE-EVT-2025-02 | 2025-06-21 | 5 | 5 | 1 | 0.988 |

## 5. Top random-forest features (24-hour model)

| Feature | Importance |
|---|---:|
| do_mg_l | 0.2516 |
| do_min3 | 0.1744 |
| do_range3 | 0.1535 |
| do_roll3_mean | 0.1197 |
| do_lag1 | 0.1003 |
| do_lag2 | 0.0522 |
| do_change_1d | 0.0515 |
| do_roll7_mean | 0.0307 |
| bod_mg_l | 0.0203 |
| water_temp_c | 0.0181 |
| temp_roll3_mean | 0.0081 |
| bod_roll3_mean | 0.0067 |

Feature importance describes this simulation only. It does not identify a real
cause of fish kills and must not be used as an ecological finding.

## 6. What this demonstrates

- The pipeline can join the synthetic base panel to weather.
- The pipeline can inject a known event process and build labels.
- The pipeline can construct backward-looking features without future leakage.
- The pipeline can split chronologically and evaluate rare-event metrics.
- The code can save quarantined model artifacts and a model card.
- The output can be audited against the synthetic event schedule.

## 7. What this does not demonstrate

- That Laguna de Bay fish kills are predictable.
- That any real station/zone has a risk level.
- That the synthetic event effect is realistic.
- That the event overlay preserves the base dataset's annual calibration; it does not.
- That the synthetic feature importances are ecological findings.
- That the metrics will transfer to real data.
- That the Section 6 model-readiness gate has passed.

## 8. Quarantine

- Data: `data/synthetic/base_model/` only.
- Models: `models/synthetic/base_model/` only.
- Every row has `data_origin = synthetic_base_v1_event_overlay`.
- No synthetic row is loaded into `dashboard/src/data/dashboard.json`.
- `models/model.joblib` remains absent.
- The real dashboard must continue to show **risk assessment unavailable**.

## 9. Files

- `data/synthetic/base_model/synthetic_events.csv`
- `data/synthetic/base_model/synthetic_modeling_dataset.csv`
- `data/synthetic/base_model/synthetic_test_predictions.csv`
- `data/synthetic/base_model/manifest.json`
- `models/synthetic/base_model/*.joblib`
- `reports/tables/synthetic_base_model_metrics.csv`
- `reports/tables/synthetic_base_model_predictions.csv`
- `reports/tables/synthetic_base_model_feature_importance.csv`
- `reports/tables/synthetic_base_event_detection.csv`
- `reports/tables/synthetic_base_model_diagnostics.csv`
- `reports/tables/synthetic_base_model_card.md`
- `reports/tables/system_gaps_and_todo.md`
