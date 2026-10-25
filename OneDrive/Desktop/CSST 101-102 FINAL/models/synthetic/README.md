# Quarantined synthetic model artifacts

> **SIMULATION ONLY — NOT EVIDENCE**

This folder contains four separate synthetic model demonstrations. None is a
real HIMPIL model.

## `base_model/` — synthetic base event-overlay models

Trained by `sandbox/synthetic/train_base_model.py` on a synthetic event overlay of
the synthetic base dataset. The base dataset itself is environmental data only;
the model exists only in this subfolder.

| Artifact | Purpose |
|---|---|
| `random_forest_24h.joblib` | 24-hour synthetic event-overlay model |
| `random_forest_48h.joblib` | 48-hour synthetic event-overlay model |
| `random_forest_72h.joblib` | 72-hour synthetic event-overlay model |
| `logistic_24h.joblib` | 24-hour baseline comparison |
| `dummy_24h.joblib` | 24-hour majority-class reference |

Report: `reports/tables/synthetic_base_model_report.md`  
Model card: `reports/tables/synthetic_base_model_card.md`

## `gap_filled/` - synthetic gap-filled models

Trained by `sandbox/synthetic/train_gap_filled_model.py` from
`data/synthetic/gap_fill/himpil_synthetic_complete.sqlite`. The database fills
the ten training checks in a synthetic scope: dated pre-event rows, exact event
dates, incident reports, no-event windows, coordinates, a zone crosswalk,
aggregation rules, and corroboration.

| Artifact | Purpose |
|---|---|
| `random_forest_24h.joblib` | 24-hour synthetic gap-filled model |
| `random_forest_48h.joblib` | 48-hour synthetic gap-filled model |
| `random_forest_72h.joblib` | 72-hour synthetic gap-filled model |
| `manifest.json` | Metrics, counts, and provenance |

Reports: `reports/tables/synthetic_gap_fill_database_report.md` and
`reports/tables/synthetic_gap_filled_model_report.md`.

## `presentation/` - five-input demonstration model

Trained by `sandbox/synthetic/train_presentation_model.py` on the same synthetic
event overlay, using only dissolved oxygen, water temperature, pH, rainfall, and
wind speed. It predicts the synthetic 72-hour event label and is intended for a
team presentation, not for evidence or a real warning. Its Low/Medium/High
display bands are illustrative. Report:
`reports/tables/synthetic_presentation_model_report.md`.

## Generic prototype models

The `.joblib` files directly in this folder were trained by
`sandbox/synthetic/run_prototype.py` on a completely generic 6-station synthetic
world. They are not derived from the base dataset.

## Prohibited use

- Do not load these artifacts into the real dashboard.
- Do not use them to produce a real risk level, warning, or advisory.
- Do not present the five-input demo bands as validated risk thresholds.
- Do not rename them to `models/model.joblib`.
- Do not describe their metrics as real HIMPIL performance.
- Do not treat them as evidence that the real model-readiness gate passed.
- Do not treat the synthetic event dates as historical incidents.

The real training and evaluation guards continue to expect `models/model.joblib`
to be absent. They must remain blocked until the real data and validation
requirements in `README_WORKPLAN.md` Section 6 are satisfied.

## Related documents

- [`../../sandbox/synthetic/README.md`](../../sandbox/synthetic/README.md)
- [`../../data/synthetic/base_model/README.md`](../../data/synthetic/base_model/README.md)
- [`../../data/synthetic/gap_fill/README.md`](../../data/synthetic/gap_fill/README.md)
- [`../../reports/tables/synthetic_base_model_report.md`](../../reports/tables/synthetic_base_model_report.md)
- [`../../reports/tables/synthetic_gap_filled_model_report.md`](../../reports/tables/synthetic_gap_filled_model_report.md)
- [`../../reports/tables/synthetic_base_model_card.md`](../../reports/tables/synthetic_base_model_card.md)
- [`../../reports/tables/synthetic_presentation_model_report.md`](../../reports/tables/synthetic_presentation_model_report.md)
- [`../../reports/tables/system_gaps_and_todo.md`](../../reports/tables/system_gaps_and_todo.md)
- [`../../reports/tables/synthetic_model_card.md`](../../reports/tables/synthetic_model_card.md)
- [`../../reports/tables/synthetic_prototype_report.md`](../../reports/tables/synthetic_prototype_report.md)
