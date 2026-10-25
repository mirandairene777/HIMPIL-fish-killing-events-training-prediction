# Synthetic base model data

> **SIMULATION ONLY - NOT EVIDENCE**

This folder contains the **event-overlay** data used by
`sandbox/synthetic/train_base_model.py`. It is derived from
`data/synthetic/base/`, but it is a separate synthetic modelling exercise.

| File | Description |
|---|---|
| `synthetic_events.csv` | Synthetic event and stress-only schedule. |
| `synthetic_modeling_dataset.csv` | Event-overlay panel, features, labels, split, and eligibility flags. Every row is marked `synthetic_base_v1_event_overlay`. |
| `synthetic_test_predictions.csv` | Held-out test probabilities and 24-hour alerts. |
| `manifest.json` | Seed, counts, source hashes, metrics, and quarantine flags. |

## Rules

- Do not copy these rows into `data/processed/`.
- Do not join them to real station measurements.
- Do not load them into the evidence dashboard.
- Do not describe the event dates as historical incidents.
- Do not treat the metrics as real HIMPIL performance.
- Do not treat the base calibration audit as validation of this event overlay; the overlay changes annual means for affected station-years.
- Do not rename a model artifact to `models/model.joblib`.

The base dataset itself remains in `data/synthetic/base/` and is unchanged.
