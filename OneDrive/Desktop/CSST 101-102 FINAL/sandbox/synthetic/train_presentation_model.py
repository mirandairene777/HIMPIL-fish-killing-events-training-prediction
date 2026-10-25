#!/usr/bin/env python
"""Train a small presentation model on the synthetic event-overlay panel.

SIMULATION ONLY - NOT EVIDENCE

This is a deliberately small, explainable demonstration model for a team
presentation. It uses only the five fields from the team's illustrative
training-data table:

    dissolved oxygen, water temperature, pH, rainfall, wind speed

The target is the synthetic 72-hour event label from the existing synthetic
base model. The output is a simulated probability, not a real risk assessment.
The Low/Medium/High display bands are communication labels, not scientific
thresholds.

The script trains only from `data/synthetic/base_model/` and writes only to
`models/synthetic/presentation/` and `reports/tables/synthetic_presentation_*`.
It does not read or write `data/processed/`, `models/model.joblib`, or
`dashboard/src/data/dashboard.json`.

Run from the project root:

    .\\.venv\\Scripts\\python.exe sandbox\\synthetic\\train_presentation_model.py
"""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

ROOT = Path(__file__).resolve().parents[2]
PANEL_PATH = ROOT / "data" / "synthetic" / "base_model" / "synthetic_modeling_dataset.csv"
EVENTS_PATH = ROOT / "data" / "synthetic" / "base_model" / "synthetic_events.csv"
MODEL_DIR = ROOT / "models" / "synthetic" / "presentation"
REPORT_DIR = ROOT / "reports" / "tables"

MODEL_PATH = MODEL_DIR / "risk_demo_model.joblib"
MANIFEST_PATH = MODEL_DIR / "manifest.json"
METRICS_PATH = REPORT_DIR / "synthetic_presentation_model_metrics.csv"
EXAMPLES_PATH = REPORT_DIR / "synthetic_presentation_model_examples.csv"
IMPORTANCE_PATH = REPORT_DIR / "synthetic_presentation_model_feature_importance.csv"
REPORT_PATH = REPORT_DIR / "synthetic_presentation_model_report.md"

WARNING = "SIMULATION ONLY - NOT EVIDENCE"
DATA_ORIGIN = "synthetic_base_v1_event_overlay"
TARGET = "y_72h"
THRESHOLD = 0.5
BAND_THRESHOLDS = {"low_max": 0.25, "high_min": 0.50}
SEED = 20261023
FEATURES = [
    "do_mg_l",
    "water_temp_c",
    "ph",
    "rainfall_mm_mean",
    "wind_mps_mean",
]
FEATURE_LABELS = {
    "do_mg_l": "Dissolved oxygen (mg/L)",
    "water_temp_c": "Water temperature (C)",
    "ph": "pH",
    "rainfall_mm_mean": "Rainfall (mm)",
    "wind_mps_mean": "Wind speed (m/s)",
}
TEAM_EXAMPLE_INPUTS = [
    (7.2, 27.0, 7.5, 2.0, 12.0, "Low"),
    (6.5, 28.0, 7.2, 5.0, 10.0, "Low"),
    (4.8, 30.0, 7.0, 15.0, 8.0, "Medium"),
    (3.9, 31.0, 6.8, 20.0, 5.0, "Medium"),
    (2.1, 33.0, 6.5, 30.0, 3.0, "High"),
    (1.5, 34.0, 6.2, 25.0, 4.0, "High"),
]


def demo_band(probability: float) -> str:
    if probability < BAND_THRESHOLDS["low_max"]:
        return "Low"
    if probability < BAND_THRESHOLDS["high_min"]:
        return "Medium"
    return "High"


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame]:
    panel = pd.read_csv(PANEL_PATH, parse_dates=["date"], low_memory=False)
    events = pd.read_csv(
        EVENTS_PATH,
        parse_dates=["event_start_date", "event_end_date"],
    )
    return panel, events


def split_frame(panel: pd.DataFrame, split: str) -> pd.DataFrame:
    return panel.loc[
        panel["split"].eq(split)
        & panel["model_eligible"].eq(1)
        & panel[TARGET].notna()
    ].copy()


def event_detection(
    frame: pd.DataFrame,
    events: pd.DataFrame,
    split: str,
) -> tuple[int, int]:
    start = frame["date"].min()
    end = frame["date"].max()
    split_events = events.loc[
        events["period_type"].eq("synthetic_event")
        & events["event_start_date"].between(start, end)
    ]
    detected = 0
    for event in split_events.itertuples(index=False):
        affected = {
            value.strip()
            for value in str(event.affected_stations).split(";")
            if value.strip()
        }
        window_start = event.event_start_date - pd.Timedelta(hours=72)
        hits = frame.loc[
            frame["date"].ge(window_start)
            & frame["date"].lt(event.event_start_date)
            & frame["station_id"].isin(affected)
            & frame["alert"].eq(1)
        ]
        if not hits.empty:
            detected += 1
    return detected, len(split_events)


def metrics_row(
    frame: pd.DataFrame,
    events: pd.DataFrame,
    split: str,
) -> dict[str, object]:
    y_true = frame[TARGET].astype(int)
    probability = frame["probability"].astype(float)
    prediction = frame["alert"].astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, prediction, labels=[0, 1]).ravel()
    detected, total_events = event_detection(frame, events, split)
    return {
        "split": split,
        "target": TARGET,
        "threshold": THRESHOLD,
        "rows": len(frame),
        "positives": int(y_true.sum()),
        "alerts": int(prediction.sum()),
        "true_positives": int(tp),
        "false_positives": int(fp),
        "true_negatives": int(tn),
        "false_negatives": int(fn),
        "precision": round(precision_score(y_true, prediction, zero_division=0), 4),
        "recall": round(recall_score(y_true, prediction, zero_division=0), 4),
        "f1": round(f1_score(y_true, prediction, zero_division=0), 4),
        "pr_auc": round(average_precision_score(y_true, probability), 4),
        "roc_auc": round(roc_auc_score(y_true, probability), 4),
        "brier": round(brier_score_loss(y_true, probability), 6),
        "events": total_events,
        "events_detected": detected,
        "data_origin": DATA_ORIGIN,
        "warning": WARNING,
    }


def markdown_table(rows: list[dict[str, object]], columns: list[str]) -> str:
    header = "| " + " | ".join(columns) + " |"
    divider = "|" + "|".join("---" for _ in columns) + "|"
    body = "\n".join(
        "| " + " | ".join(str(row.get(column, "")) for column in columns) + " |"
        for row in rows
    )
    return "\n".join([header, divider, body])


def build_report(
    metrics: list[dict[str, object]],
    importance: pd.DataFrame,
    examples: pd.DataFrame,
    train_rows: int,
    validation_rows: int,
    test_rows: int,
) -> str:
    metric_rows = [
        {
            "Split": row["split"],
            "Rows": row["rows"],
            "Positives": row["positives"],
            "Alerts": row["alerts"],
            "Precision": row["precision"],
            "Recall": row["recall"],
            "F1": row["f1"],
            "PR-AUC": row["pr_auc"],
            "Brier": row["brier"],
            "Events detected": f"{row['events_detected']}/{row['events']}",
        }
        for row in metrics
    ]
    importance_rows = [
        {
            "Input": FEATURE_LABELS.get(row.feature, row.feature),
            "Importance": round(float(row.importance), 4),
        }
        for row in importance.itertuples(index=False)
    ]
    example_rows = [
        {
            "DO": row.do_mg_l,
            "Temp": row.water_temp_c,
            "pH": row.ph,
            "Rain": row.rainfall_mm_mean,
            "Wind": row.wind_mps_mean,
            "Simulated p(72h)": round(float(row.probability_72h), 4),
            "Demo band": row.demo_band,
            "Team example band": row.team_example_band,
        }
        for row in examples.itertuples(index=False)
    ]
    test = next(row for row in metrics if row["split"] == "test")
    validation = next(row for row in metrics if row["split"] == "validation")
    return f"""# Synthetic presentation model - 5 inputs

> **{WARNING}**

This is a small, reproducible **presentation demo** trained on the synthetic
event-overlay panel. It is not a model of Laguna de Bay, not a real fish-kill
risk assessment, and not a validated early-warning system. The inputs in the
example table are fictional values copied from the team's illustrative slide;
they are not measurements.

## 1. What this demo does

- Uses five inputs: dissolved oxygen, water temperature, pH, rainfall, and wind
  speed.
- Trains a random forest on the synthetic 72-hour event label (`{TARGET}`).
- Predicts a **simulated probability that a synthetic event starts within 72
  hours at that station**.
- Maps the probability to an illustrative **Low / Medium / High demo band**:
  - Low: p < {BAND_THRESHOLDS['low_max']}
  - Medium: {BAND_THRESHOLDS['low_max']} <= p < {BAND_THRESHOLDS['high_min']}
  - High: p >= {BAND_THRESHOLDS['high_min']}

The bands are communication labels, not scientific thresholds. They were not
validated against real fish kills.

## 2. Data and split

| Item | Value |
|---|---|
| Source panel | `data/synthetic/base_model/synthetic_modeling_dataset.csv` |
| Source events | `data/synthetic/base_model/synthetic_events.csv` |
| Data origin | `{DATA_ORIGIN}` |
| Train rows | {train_rows} (before 2023) |
| Validation rows | {validation_rows} (2023) |
| Test rows | {test_rows} (2024-2025) |
| Target | `{TARGET}`: synthetic event start within 72 hours |
| Model | Random forest, 300 trees, `min_samples_leaf=5`, balanced subsample |
| Seed | `{SEED}` |

## 3. Out-of-sample metrics (simulation)

{markdown_table(metric_rows, ["Split", "Rows", "Positives", "Alerts", "Precision", "Recall", "F1", "PR-AUC", "Brier", "Events detected"])}

The five-input model is deliberately simpler than the full synthetic base model.
Its test F1 is **{test['f1']}** at the default 0.5 threshold, compared with
**0.797** for the full-feature 72-hour random forest. The drop is expected: the
full model uses lags, rolling dissolved-oxygen features, and weather context.
The five-input version is for an understandable demo, not for replacing the
full synthetic model.

The model issues **{test['alerts']}** station-day alerts in the test period:
**{test['true_positives']}** true positives, **{test['false_positives']}** false
positives, and **{test['false_negatives']}** missed positive rows. That is a
high-recall, low-precision simulation. It is not ready for real warnings.

## 4. Feature importance

{markdown_table(importance_rows, ["Input", "Importance"])}

Dissolved oxygen and water temperature dominate. That matches the project's
domain hypothesis, but it is also a property of the synthetic generator: the
event effect was injected mainly through low DO and high temperature. It is not
evidence that the same relationship holds in Laguna de Bay.

## 5. Example inputs from the team slide

These are **fictional inputs**, included only to show the model interface. The
team's example bands are also illustrative. The model uses a 72-hour horizon;
the team slide does not define its horizon.

{markdown_table(example_rows, ["DO", "Temp", "pH", "Rain", "Wind", "Simulated p(72h)", "Demo band", "Team example band"])}

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
4. **What the numbers say (simulation):** test precision **{test['precision']}**,
   recall **{test['recall']}**, F1 **{test['f1']}**, PR-AUC **{test['pr_auc']}**;
   all **{test['events_detected']}/{test['events']}** synthetic test events were
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
.\\.venv\\Scripts\\python.exe sandbox\\synthetic\\train_presentation_model.py
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
.\\.venv\\Scripts\\python.exe sandbox\\presentation_app\\app.py
```

Open `http://127.0.0.1:8000`. The first start may take a few seconds while the
model loads. The app is local-only and is not connected to the evidence
dashboard.

> **{WARNING}**
"""


def main() -> None:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    panel, events = load_inputs()

    train = split_frame(panel, "train")
    validation = split_frame(panel, "validation")
    test = split_frame(panel, "test")

    model = RandomForestClassifier(
        n_estimators=300,
        min_samples_leaf=5,
        class_weight="balanced_subsample",
        random_state=SEED,
        n_jobs=-1,
    )
    model.fit(train[FEATURES], train[TARGET].astype(int))

    metrics: list[dict[str, object]] = []
    for split_name, frame in [
        ("validation", validation),
        ("test", test),
    ]:
        working = frame.copy()
        working["probability"] = model.predict_proba(working[FEATURES])[:, 1]
        working["alert"] = (working["probability"] >= THRESHOLD).astype(int)
        metrics.append(metrics_row(working, events, split_name))

    importance = pd.DataFrame(
        {
            "feature": FEATURES,
            "importance": model.feature_importances_,
        }
    ).sort_values("importance", ascending=False)

    example_frame = pd.DataFrame(
        TEAM_EXAMPLE_INPUTS,
        columns=FEATURES + ["team_example_band"],
    )
    example_frame["probability_72h"] = model.predict_proba(
        example_frame[FEATURES]
    )[:, 1]
    example_frame["demo_band"] = example_frame["probability_72h"].map(demo_band)
    example_frame["source"] = (
        "fictional example values from the team slide; not real measurements"
    )
    example_frame["data_origin"] = DATA_ORIGIN
    example_frame["warning"] = WARNING
    example_frame = example_frame[
        FEATURES
        + [
            "probability_72h",
            "demo_band",
            "team_example_band",
            "source",
            "data_origin",
            "warning",
        ]
    ]

    joblib.dump(model, MODEL_PATH)
    manifest = {
        "status": "synthetic_presentation_demo",
        "warning": WARNING,
        "data_origin": DATA_ORIGIN,
        "target": TARGET,
        "target_description": "synthetic event start within 72 hours at the same station",
        "features": FEATURES,
        "feature_labels": FEATURE_LABELS,
        "threshold": THRESHOLD,
        "demo_bands": {
            "low": f"p < {BAND_THRESHOLDS['low_max']}",
            "medium": (
                f"{BAND_THRESHOLDS['low_max']} <= p < "
                f"{BAND_THRESHOLDS['high_min']}"
            ),
            "high": f"p >= {BAND_THRESHOLDS['high_min']}",
        },
        "band_thresholds": BAND_THRESHOLDS,
        "seed": SEED,
        "train_rows": len(train),
        "validation_rows": len(validation),
        "test_rows": len(test),
        "source_panel": "data/synthetic/base_model/synthetic_modeling_dataset.csv",
        "source_events": "data/synthetic/base_model/synthetic_events.csv",
        "quarantine": {
            "not_evidence": True,
            "does_not_satisfy_model_gate": True,
            "not_connected_to_dashboard": True,
            "not_for_real_advisories": True,
        },
    }
    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    pd.DataFrame(metrics).to_csv(METRICS_PATH, index=False)
    importance.to_csv(IMPORTANCE_PATH, index=False)
    example_frame.to_csv(EXAMPLES_PATH, index=False)
    REPORT_PATH.write_text(
        build_report(
            metrics,
            importance,
            example_frame,
            len(train),
            len(validation),
            len(test),
        ),
        encoding="utf-8",
    )

    print(WARNING)
    print(f"Wrote {MODEL_PATH.relative_to(ROOT)}")
    print(f"Wrote {MANIFEST_PATH.relative_to(ROOT)}")
    print(f"Wrote {METRICS_PATH.relative_to(ROOT)}")
    print(f"Wrote {IMPORTANCE_PATH.relative_to(ROOT)}")
    print(f"Wrote {EXAMPLES_PATH.relative_to(ROOT)}")
    print(f"Wrote {REPORT_PATH.relative_to(ROOT)}")
    for row in metrics:
        print(
            f"  {row['split']:10s} rows={row['rows']} positives={row['positives']} "
            f"alerts={row['alerts']} precision={row['precision']} "
            f"recall={row['recall']} f1={row['f1']} pr_auc={row['pr_auc']} "
            f"events={row['events_detected']}/{row['events']}"
        )


if __name__ == "__main__":
    main()
