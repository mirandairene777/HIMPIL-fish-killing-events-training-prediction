# Synthetic base-model artifacts

> **SIMULATION ONLY — NOT EVIDENCE**

Models trained by `sandbox/synthetic/train_base_model.py` on a synthetic event
overlay of `data/synthetic/base/`.

| File | Description |
|---|---|
| `random_forest_24h.joblib` | 24-hour random forest |
| `random_forest_48h.joblib` | 48-hour random forest |
| `random_forest_72h.joblib` | 72-hour random forest |
| `logistic_24h.joblib` | 24-hour logistic baseline |
| `dummy_24h.joblib` | 24-hour majority-class reference |

These are not real HIMPIL models. Do not load them into the evidence dashboard,
rename them to `models/model.joblib`, or use them for a real advisory.

See [`../README.md`](../README.md),
[`../../../reports/tables/synthetic_base_model_report.md`](../../../reports/tables/synthetic_base_model_report.md),
and [`../../../reports/tables/synthetic_base_model_card.md`](../../../reports/tables/synthetic_base_model_card.md).
