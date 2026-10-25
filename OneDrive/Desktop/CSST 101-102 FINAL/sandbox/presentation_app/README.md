# HIMPIL presentation demo app

> **Synthetic demo**

A local web app for the five-input synthetic presentation model. It loads
`models/synthetic/presentation/risk_demo_model.joblib` and returns a simulated
72-hour event probability with an illustrative Low/Medium/High band.

This is a **team presentation aid**, not a real fish-kill risk assessment. It is
not connected to the evidence dashboard and writes no data.

## Run

From the repository root:

```powershell
.\.venv\Scripts\python.exe sandbox\presentation_app\app.py
```

Open:

```text
http://127.0.0.1:8000
```

If the port is busy:

```powershell
.\.venv\Scripts\python.exe sandbox\presentation_app\app.py --port 8001
```

Press `Ctrl+C` to stop the server.

## What it shows

- Five inputs: dissolved oxygen, water temperature, pH, rainfall, and wind speed.
- A simulated probability that a synthetic event starts within 72 hours.
- An illustrative demo band:
  - Low: p < 0.25
  - Medium: 0.25 <= p < 0.50
  - High: p >= 0.50
- One compact **Synthetic demo** badge on every page.

The example values are fictional. They are included only to show the interface.

## What it does not do

- It does not predict real fish kills.
- It does not provide a real risk level, advisory, or early warning.
- It does not use real station data or a real map.
- It does not read or write `dashboard/src/data/dashboard.json`.
- It does not replace the model-readiness gate.

## Why the standard library

The app uses `http.server` so it runs with the existing environment. There is no
Flask, FastAPI, Streamlit, or JavaScript build step to install.

## Files

| File | Purpose |
|---|---|
| `app.py` | Local HTTP server and HTML interface |
| `../synthetic/predict_presentation.py` | Reusable prediction function and CLI |
| `../../models/synthetic/presentation/risk_demo_model.joblib` | Saved synthetic model |
| `../../models/synthetic/presentation/manifest.json` | Features, target, bands, and quarantine flags |

## Checks

```powershell
.\.venv\Scripts\python.exe -m py_compile sandbox\presentation_app\app.py
curl.exe -s http://127.0.0.1:8000/health
```

The `/health` endpoint returns `{"status": "ok", "mode": "synthetic_demo"}`.

Do not deploy this app as a public risk or advisory service.
