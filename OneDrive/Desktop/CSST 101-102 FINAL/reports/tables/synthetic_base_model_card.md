# Synthetic base model card

> **SIMULATION ONLY - NOT EVIDENCE**

## Model details

- **Name:** HIMPIL synthetic base model demonstration.
- **Version:** 1.0.
- **Generated (UTC):** 2026-10-24T13:41:59+00:00.
- **Code:** `sandbox/synthetic/train_base_model.py`.
- **Artifacts:** `models/synthetic/base_model/`.
- **Data:** `data/synthetic/base/` plus a separate synthetic event overlay.
- **Seed:** `20261023`.

## Intended use

- Test the HIMPIL modelling pipeline end to end.
- Demonstrate chronological splitting, rare-event metrics, and event-level
  detection.
- Support internal code review, onboarding, and UI discussions.
- Show how a future model card and report could be structured.

## Prohibited use

- Do not use for a real fish-kill warning, advisory, or public risk category.
- Do not describe the metrics as HIMPIL's real performance.
- Do not load these artifacts into the evidence dashboard.
- Do not rename an artifact to `models/model.joblib`.
- Do not use the model to make decisions about real stations, fishers, or LGUs.
- Do not treat synthetic feature importance as an ecological finding.

## Data and target

- 15 real lake station labels; daily values are synthetic.
- 2016-2025 synthetic calendar.
- Synthetic events are injected into a copy of the base panel.
- Target: event start within 24, 48, or 72 hours at the same station.
- During-event and recovery rows are excluded from fitting/evaluation.

## Test metrics (simulation only)

| Horizon (h) | Positives | Precision | Recall | F1 | PR-AUC | ROC-AUC | Brier |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 24 | 20 | 0.455 | 1.000 | 0.625 | 0.568 | 0.999 | 0.0020 |
| 48 | 40 | 0.597 | 1.000 | 0.748 | 0.957 | 1.000 | 0.0021 |
| 72 | 60 | 0.670 | 0.983 | 0.797 | 0.947 | 1.000 | 0.0026 |

Top five features by random-forest importance: do_mg_l, do_min3, do_range3, do_roll3_mean, do_lag1.

These metrics are optimistic by construction. The event effect is injected into
the same variables used as features. Real performance cannot be inferred.

## Limitations

- No real daily observations, verified events, credible negatives, coordinates,
  or station-to-zone crosswalk.
- Event dates, event effects, labels, and stress-only periods are synthetic.
- Annual mean calibration does not guarantee realistic daily distributions,
  extremes, autocorrelation, or cross-variable dependence.
- The event overlay changes annual means for affected station-years; the base
  calibration audit does not apply to the overlay.
- Weather zones are synthetic; the model uses a network mean of three zones.
- Test positives are few; confidence intervals would be wide.
- No external validation, prospective evaluation, probability calibration, or
  threshold policy.
- No causal interpretation.
- The Section 6 gate remains unmet.

## Maintenance

Regenerate with:

```powershell
.\.venv\Scripts\python.exe sandbox\synthetic\build_base_dataset.py
.\.venv\Scripts\python.exe sandbox\synthetic\train_base_model.py
```

Any change to the event schedule, features, split, or threshold requires a new
version and a new report.
