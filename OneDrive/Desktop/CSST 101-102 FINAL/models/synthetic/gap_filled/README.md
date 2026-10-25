# Synthetic gap-filled model artifacts

This folder contains random-forest models trained from the synthetic gap-filled
database. They are separate from the real evidence model and are used for the
dashboard's labeled synthetic training panel.

| File | Horizon |
|---|---|
| `random_forest_24h.joblib` | 24 hours |
| `random_forest_48h.joblib` | 48 hours |
| `random_forest_72h.joblib` | 72 hours |
| `manifest.json` | Metrics, counts, paths, and provenance |

Regenerate with:

```powershell
.\.venv\Scripts\python.exe sandbox\synthetic\build_gap_filled_database.py
.\.venv\Scripts\python.exe sandbox\synthetic\train_gap_filled_model.py
```
