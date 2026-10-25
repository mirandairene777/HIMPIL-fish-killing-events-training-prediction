# Synthetic gap-filled model report

**Generated (UTC):** 2026-10-24T14:39:51+00:00  
**Code:** `sandbox/synthetic/train_gap_filled_model.py`  
**Database:** `data/synthetic/gap_fill/himpil_synthetic_complete.sqlite`  
**Model card:** `reports/tables/synthetic_gap_filled_model_card.md`  
**Scope:** synthetic training demonstration

## 1. What was trained

- **Input table:** `modeling_dataset` in the gap-filled SQLite database.
- **Coverage:** 15 stations, 2016-2025, 54,795 station-days.
- **Events:** 20 exact-dated synthetic fish-kill events across 10 years.
- **Pre-event evidence:** 400 dated rows before the events.
- **Non-event windows:** 1,700 synthetic monthly patrol windows.
- **Corroboration:** 40 independent synthetic source records.
- **Coordinates and zones:** 15 coordinates and 15 zone assignments.
- **Readiness:** 10/10 checks pass in the synthetic scope.
- **Targets:** event start within 24, 48, or 72 hours at the same station.
- **Split:** chronological. Train before 2023; validation 2023; test 2024-2025.
- **Model:** random forest, 300 trees, max depth 6, minimum leaf 5.

## 2. Test results

| Horizon (h) | Pos | Neg | Precision | Recall | F1 | PR-AUC | ROC-AUC | Brier | TP | FP | FN | TN |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 24 | 20 | 10785 | 0.465 | 1.000 | 0.635 | 0.603 | 0.999 | 0.0020 | 20 | 23 | 0 | 10762 |
| 48 | 40 | 10765 | 0.606 | 1.000 | 0.755 | 0.941 | 1.000 | 0.0021 | 40 | 26 | 0 | 10739 |
| 72 | 60 | 10745 | 0.670 | 0.983 | 0.797 | 0.939 | 1.000 | 0.0029 | 59 | 29 | 1 | 10716 |

## 3. Event-level detection (24-hour model, test)

| Event | Start | Prediction rows | Alerts | Alerted any | Max probability |
|---|---|---:|---:|---:|---:|
| SYN-BASE-EVT-2024-01 | 2024-03-15 | 5 | 5 | 1 | 0.998 |
| SYN-BASE-EVT-2024-02 | 2024-06-16 | 5 | 5 | 1 | 0.626 |
| SYN-BASE-EVT-2025-01 | 2025-03-18 | 5 | 5 | 1 | 0.995 |
| SYN-BASE-EVT-2025-02 | 2025-06-21 | 5 | 5 | 1 | 0.978 |

## 4. Top features (72-hour model)

| Feature | Importance |
|---|---:|
| do_range3 | 0.2701 |
| do_mg_l | 0.2017 |
| do_change_1d | 0.1476 |
| do_min3 | 0.1236 |
| do_roll3_mean | 0.0565 |
| do_lag1 | 0.0481 |
| bod_mg_l | 0.0352 |
| water_temp_c | 0.0337 |

## 5. What this demonstrates

The pipeline can load a complete synthetic database, build chronological
splits, train 24/48/72-hour models, evaluate rare-event metrics, detect
events, and save artifacts. The database fills the structural gaps that block
the real pipeline, so this is an end-to-end exercise of the training system.

## 6. Boundary

The values, event dates, incident reports, corroboration, coordinates, zones,
and non-event windows are synthetic. The real evidence gate remains
2 pass and 8 fail, and the
real dashboard still reports **risk assessment unavailable**. This model is a
demonstration, not a real Laguna de Bay advisory.

## 7. Files

- `models/synthetic/gap_filled/random_forest_24h.joblib`
- `models/synthetic/gap_filled/random_forest_48h.joblib`
- `models/synthetic/gap_filled/random_forest_72h.joblib`
- `reports/tables/synthetic_gap_filled_model_metrics.csv`
- `reports/tables/synthetic_gap_filled_test_predictions.csv`
- `reports/tables/synthetic_gap_filled_event_detection.csv`
- `reports/tables/synthetic_gap_filled_feature_importance.csv`
- `dashboard/src/data/syntheticDemo.json`
