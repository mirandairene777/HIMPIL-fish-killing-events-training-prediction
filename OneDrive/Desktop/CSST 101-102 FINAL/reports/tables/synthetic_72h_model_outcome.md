# Synthetic 72-hour model outcome

> **SIMULATION ONLY - NOT EVIDENCE**
>
> This model is trained on synthetic daily data calibrated to the supplied
> annual water-quality and monthly weather summaries. It is not a real
> Laguna de Bay fish-kill model and must not be used for a real warning.

**Status:** Trained and rerun on 2026-10-24  
**Training command:** `.venv\Scripts\python.exe sandbox\synthetic\train_base_model.py`  
**Model:** `models/synthetic/base_model/random_forest_72h.joblib`  
**Full report:** `reports/tables/synthetic_base_model_report.md`  
**Model card:** `reports/tables/synthetic_base_model_card.md`

## 1. What the model was trained on

- 15 real lake-station labels from the supplied LLDA workbooks.
- Calendar 2016-01-01 to 2025-12-31.
- **900** annual station-year-variable anchors:
  - **711** real numeric anchors;
  - **189** synthetic imputed anchors;
  - **90** 2025 anchors with unverified completeness.
- Annual calibration error: mean absolute error **0.000047**, maximum absolute
  error **0.000464**.
- Daily water quality and weather values are synthetic.
- **54,795** synthetic panel rows; **53,950** model-eligible rows.
- **20** synthetic event periods and **10** stress-only/no-event periods.
- Chronological split: train before 2023, validation in 2023, test in 2024-2025.
- Target: synthetic fish-kill event start within **72 hours** at the same station.
- Features: current conditions, backward-looking lags, rolling means, and
  rainfall/wind/nutrient summaries. No future values are used.

## 2. Test result at the 72-hour horizon

Random forest, test partition, threshold 0.5:

| Metric | Value |
|---|---:|
| Test rows | 10,805 |
| Positive rows | 60 |
| Negative rows | 10,745 |
| Accuracy | 0.9972 |
| Precision | 0.6705 |
| Recall | 0.9833 |
| F1 | 0.7973 |
| PR-AUC | 0.9471 |
| ROC-AUC | 0.9995 |
| Brier score | 0.0026 |
| True positives | 59 |
| False positives | 29 |
| False negatives | 1 |
| True negatives | 10,716 |

**Event-level check:** the 72-hour model detected **4 of 4** synthetic test
events from pre-event rows, using the 0.5 probability threshold.

## 3. What this outcome demonstrates

- The synthetic base can be generated from the supplied annual/monthly data and
  the real station-year frame.
- The pipeline can build leakage-aware 72-hour labels and backward-looking
  features.
- The model can be trained, saved, evaluated, and audited with a chronological
  split.
- The saved artifact can be reloaded for presentation or software testing.
- The synthetic event schedule can be used to check event-level detection, not
  only row-level metrics.

## 4. What this outcome does not demonstrate

- That Laguna de Bay fish kills are predictable.
- That the synthetic event effect is realistic.
- That the 72-hour probabilities will transfer to real observations.
- That the model has passed the real model-readiness gate.
- That the model can support a real advisory, zone map, or SMS alert.

The real dashboard continues to report **risk assessment unavailable**. The
synthetic artifact is quarantined under `models/synthetic/base_model/` and is
not loaded into `dashboard/src/data/dashboard.json`.
