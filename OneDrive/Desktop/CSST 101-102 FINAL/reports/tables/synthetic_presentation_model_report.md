# Synthetic presentation model - 5 inputs

> **SIMULATION ONLY - NOT EVIDENCE**

This is a small, reproducible **presentation demo** trained on the synthetic
event-overlay panel. It is not a model of Laguna de Bay, not a real fish-kill
risk assessment, and not a validated early-warning system. The inputs in the
example table are fictional values copied from the team's illustrative slide;
they are not measurements.

## 1. What this demo does

- Uses five inputs: dissolved oxygen, water temperature, pH, rainfall, and wind
  speed.
- Trains a random forest on the synthetic 72-hour event label (`y_72h`).
- Predicts a **simulated probability that a synthetic event starts within 72
  hours at that station**.
- Maps the probability to an illustrative **Low / Medium / High demo band**:
  - Low: p < 0.25
  - Medium: 0.25 <= p < 0.5
  - High: p >= 0.5

The bands are communication labels, not scientific thresholds. They were not
validated against real fish kills.

## 2. Data and split

| Item | Value |
|---|---|
| Source panel | `data/synthetic/base_model/synthetic_modeling_dataset.csv` |
| Source events | `data/synthetic/base_model/synthetic_events.csv` |
| Data origin | `synthetic_base_v1_event_overlay` |
| Train rows | 37750 (before 2023) |
| Validation rows | 5395 (2023) |
| Test rows | 10805 (2024-2025) |
| Target | `y_72h`: synthetic event start within 72 hours |
| Model | Random forest, 300 trees, `min_samples_leaf=5`, balanced subsample |
| Seed | `20261023` |

## 3. Out-of-sample metrics (simulation)

| Split | Rows | Positives | Alerts | Precision | Recall | F1 | PR-AUC | Brier | Events detected |
|---|---|---|---|---|---|---|---|---|---|
| validation | 5395 | 30 | 21 | 0.8571 | 0.6 | 0.7059 | 0.7451 | 0.002491 | 2/2 |
| test | 10805 | 60 | 124 | 0.4032 | 0.8333 | 0.5435 | 0.6947 | 0.006542 | 4/4 |

The five-input model is deliberately simpler than the full synthetic base model.
Its test F1 is **0.5435** at the default 0.5 threshold, compared with
**0.797** for the full-feature 72-hour random forest. The drop is expected: the
full model uses lags, rolling dissolved-oxygen features, and weather context.
The five-input version is for an understandable demo, not for replacing the
full synthetic model.

The model issues **124** station-day alerts in the test period:
**50** true positives, **74** false
positives, and **10** missed positive rows. That is a
high-recall, low-precision simulation. It is not ready for real warnings.

## 4. Feature importance

| Input | Importance |
|---|---|
| Dissolved oxygen (mg/L) | 0.6262 |
| Water temperature (C) | 0.2494 |
| pH | 0.0462 |
| Wind speed (m/s) | 0.0397 |
| Rainfall (mm) | 0.0385 |

Dissolved oxygen and water temperature dominate. That matches the project's
domain hypothesis, but it is also a property of the synthetic generator: the
event effect was injected mainly through low DO and high temperature. It is not
evidence that the same relationship holds in Laguna de Bay.

## 5. Example inputs from the team slide

These are **fictional inputs**, included only to show the model interface. The
team's example bands are also illustrative. The model uses a 72-hour horizon;
the team slide does not define its horizon.

| DO | Temp | pH | Rain | Wind | Simulated p(72h) | Demo band | Team example band |
|---|---|---|---|---|---|---|---|
| 7.2 | 27.0 | 7.5 | 2.0 | 12.0 | 0.0033 | Low | Low |
| 6.5 | 28.0 | 7.2 | 5.0 | 10.0 | 0.0811 | Low | Low |
| 4.8 | 30.0 | 7.0 | 15.0 | 8.0 | 0.4588 | Medium | Medium |
| 3.9 | 31.0 | 6.8 | 20.0 | 5.0 | 0.6366 | High | Medium |
| 2.1 | 33.0 | 6.5 | 30.0 | 3.0 | 0.773 | High | High |
| 1.5 | 34.0 | 6.2 | 25.0 | 4.0 | 0.6699 | High | High |

The model agrees with five of the six illustrative bands. The fourth row is a
useful teaching point: changing the band thresholds changes the label, and the
team's fictional labels were not derived from a validated rule. Do not present
the table as an accuracy check.

## 6. Five-minute presentation script

1. **What HIMPIL is meant to do:** combine water-quality and weather data to
   give fish-pen operators earlier information about fish-kill risk.
2. **What we built:** a reproducible synthetic pipeline and this five-input
   demo model. It is trained and runnable.
3. **What the model does:** estimates a simulated 72-hour event probability and
   maps it to an illustrative Low/Medium/High band.
4. **What the numbers say (simulation):** test precision **0.4032**,
   recall **0.8333**, F1 **0.5435**, PR-AUC **0.6947**;
   all **4/4** synthetic test events were
   detected by at least one alert. These are not real performance numbers.
5. **What the data show us:** DO and water temperature dominate the synthetic
   model, which is consistent with the hypothesis but circular because the
   event effect was injected through those variables.
6. **Why we are not claiming a real warning system:** the real inputs are annual
   water summaries and monthly weather; there is one reported event, zero
   verified events, zero pre-event observations, and no authoritative zone
   crosswalk. The next step is daily data and verified event records, not more
   tuning of a synthetic model.
7. **Ask for the team:** approve the data-request list and help obtain daily
   DO/temperature/pH/rainfall/wind, event dates, station coordinates, and
   negative-window records.

## 7. What this demo does not prove

- It does not predict real fish kills.
- It does not provide real risk levels or advisories.
- It does not show that the team's fictional risk bands are correct.
- It does not satisfy the Section 6 model-readiness gate.
- It does not make the evidence dashboard any more certain; the dashboard still
  says **risk assessment unavailable**.

## 8. Reproduce

```powershell
.\.venv\Scripts\python.exe sandbox\synthetic\train_presentation_model.py
```

Outputs:

| Output | Path |
|---|---|
| Model | `models/synthetic/presentation/risk_demo_model.joblib` |
| Manifest | `models/synthetic/presentation/manifest.json` |
| Metrics | `reports/tables/synthetic_presentation_model_metrics.csv` |
| Feature importance | `reports/tables/synthetic_presentation_model_feature_importance.csv` |
| Example inputs | `reports/tables/synthetic_presentation_model_examples.csv` |
| This report | `reports/tables/synthetic_presentation_model_report.md` |

## 9. Interactive demo

A local browser version is available at `sandbox/presentation_app/app.py`. It uses
the standard library, loads the same saved model, and writes no data.

```powershell
.\.venv\Scripts\python.exe sandbox\presentation_app\app.py
```

Open `http://127.0.0.1:8000`. The first start may take a few seconds while the
model loads. The app is local-only and is not connected to the evidence
dashboard.

> **SIMULATION ONLY - NOT EVIDENCE**
