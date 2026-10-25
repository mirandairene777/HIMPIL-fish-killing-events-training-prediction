# Synthetic gap-filled model card

**Generated (UTC):** 2026-10-24T14:39:51+00:00  
**Status:** synthetic gap-fill demonstration  
**Data origin:** `synthetic_gap_fill_v1`

## Model details

- **Name:** HIMPIL synthetic gap-filled random forest.
- **Artifacts:** `models/synthetic/gap_filled/`.
- **Data:** `data/synthetic/gap_fill/himpil_synthetic_complete.sqlite`.
- **Seed:** `20261024`.
- **Targets:** synthetic event start within 24, 48, or 72 hours at the same station.
- **Readiness:** 10/10 synthetic checks pass.

## Intended use

- Exercise the full HIMPIL database-to-model pipeline.
- Demonstrate chronological splitting, rare-event metrics, event detection, and
  artifact creation when the structural data requirements are present.
- Support software review, onboarding, and UI demonstrations.

## Prohibited use

- Do not use for a real fish-kill warning, advisory, or public risk category.
- Do not describe these metrics as HIMPIL's real performance.
- Do not replace `models/model.joblib` with this artifact.
- Do not load synthetic rows into `dashboard/src/data/dashboard.json`.
- Do not treat synthetic coordinates, zones, incidents, or corroboration as
  real Laguna de Bay records.

## Test metrics

| Horizon (h) | Positives | Precision | Recall | F1 | PR-AUC | ROC-AUC | Brier |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 24 | 20 | 0.465 | 1.000 | 0.635 | 0.603 | 0.999 | 0.0020 |
| 48 | 40 | 0.606 | 1.000 | 0.755 | 0.941 | 1.000 | 0.0021 |
| 72 | 60 | 0.670 | 0.983 | 0.797 | 0.939 | 1.000 | 0.0029 |

The event effect is injected into the same variables used as features, so these
scores are optimistic by construction. The real evidence gate remains
2 pass and 8 fail.

## Maintenance

Regenerate with:

```powershell
.\.venv\Scripts\python.exe sandbox\synthetic\build_gap_filled_database.py
.\.venv\Scripts\python.exe sandbox\synthetic\train_gap_filled_model.py
```
