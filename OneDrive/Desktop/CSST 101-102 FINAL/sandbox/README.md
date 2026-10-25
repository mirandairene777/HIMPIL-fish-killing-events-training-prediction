# HIMPIL sandbox

This folder contains **non-evidence prototypes**. Nothing here is a finding
about Laguna de Bay, and nothing here may be connected to the evidence dashboard
or used to issue a warning.

Current contents:

- [`synthetic/`](synthetic/README.md) — a quarantined synthetic base dataset
  on the real station/year/schema frame, a separate base-model event overlay,
  and a generic end-to-end model demonstration built on generated station-day
  data.

- [`synthetic/train_presentation_model.py`](synthetic/train_presentation_model.py)
  and [`synthetic/predict_presentation.py`](synthetic/predict_presentation.py) -
  a five-input presentation model for team demos. It is simulation only, not
  evidence, and is not connected to the evidence dashboard.

- [`presentation_app/`](presentation_app/README.md) - a local browser demo for
  the five-input model. It uses the saved synthetic model, shows the
  **SIMULATION ONLY - NOT EVIDENCE** warning, writes no data, and is separate
  from the evidence dashboard.

The sandbox exists because the real-data model is still blocked. It lets the team
test code, review a model card, and discuss interface behavior without pretending
that the evidence gap has been closed.

> **SIMULATION ONLY — NOT EVIDENCE**

The real-data guard scripts (`python/train_model.py` and
`python/evaluate_model.py`) remain the authority for the real study. They still
refuse to train or evaluate because the Section 6 model-readiness gate has not
passed.
