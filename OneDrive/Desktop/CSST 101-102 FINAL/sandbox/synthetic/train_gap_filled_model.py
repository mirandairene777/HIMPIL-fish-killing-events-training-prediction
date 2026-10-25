"""Train HIMPIL fish-kill models from the synthetic gap-filled database.

The database supplies 24/48/72-hour labels, dated pre-event rows, exact-dated
synthetic events, credible no-event windows, coordinates, a zone crosswalk,
aggregation rules, and independent corroboration. Everything is synthetic.

Run from the project root:
    .venv\\Scripts\\python.exe sandbox\\synthetic\\train_gap_filled_model.py
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

ROOT = Path(__file__).resolve().parents[2]
GAP_FILL_DIR = ROOT / "data" / "synthetic" / "gap_fill"
DATABASE = GAP_FILL_DIR / "himpil_synthetic_complete.sqlite"
MODEL_DIR = ROOT / "models" / "synthetic" / "gap_filled"
TABLES = ROOT / "reports" / "tables"
DASHBOARD_DATA = ROOT / "dashboard" / "src" / "data" / "syntheticDemo.json"
BASE_MANIFEST = ROOT / "data" / "synthetic" / "base" / "manifest.json"
REAL_GATE = ROOT / "data" / "outputs" / "training_status.csv"
REAL_DASHBOARD = ROOT / "dashboard" / "src" / "data" / "dashboard.json"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from train_base_model import FEATURES, HORIZONS, score_predictions  # noqa: E402

DEFAULT_SEED = 20261024
WARNING = "SYNTHETIC GAP-FILL - DEMONSTRATION ONLY"
DATA_ORIGIN = "synthetic_gap_fill_v1"


def _relative(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_dataset() -> tuple[pd.DataFrame, dict[str, int]]:
    if not DATABASE.exists():
        raise FileNotFoundError(
            "Build the synthetic gap-filled database first: "
            "sandbox\\synthetic\\build_gap_filled_database.py"
        )
    with sqlite3.connect(DATABASE) as connection:
        panel = pd.read_sql_query("SELECT * FROM modeling_dataset", connection)
        counts = {
            "stations": int(
                pd.read_sql_query("SELECT COUNT(*) AS n FROM stations", connection).iloc[0]["n"]
            ),
            "incident_reports": int(
                pd.read_sql_query(
                    "SELECT COUNT(*) AS n FROM incident_reports WHERE reported_fish_kill = 1",
                    connection,
                ).iloc[0]["n"]
            ),
            "stress_reports": int(
                pd.read_sql_query(
                    "SELECT COUNT(*) AS n FROM incident_reports "
                    "WHERE period_type = 'synthetic_stress_without_event'",
                    connection,
                ).iloc[0]["n"]
            ),
            "corroboration_records": int(
                pd.read_sql_query("SELECT COUNT(*) AS n FROM corroboration", connection).iloc[0]["n"]
            ),
            "negative_windows": int(
                pd.read_sql_query("SELECT COUNT(*) AS n FROM negative_windows", connection).iloc[0]["n"]
            ),
            "pre_event_rows": int(
                pd.read_sql_query("SELECT COUNT(*) AS n FROM pre_event_observations", connection).iloc[0]["n"]
            ),
            "aggregation_rules": int(
                pd.read_sql_query("SELECT COUNT(*) AS n FROM aggregation_rules", connection).iloc[0]["n"]
            ),
            "readiness_checks": int(
                pd.read_sql_query("SELECT COUNT(*) AS n FROM readiness_checks", connection).iloc[0]["n"]
            ),
            "readiness_passed": int(
                pd.read_sql_query(
                    "SELECT COUNT(*) AS n FROM readiness_checks "
                    "WHERE synthetic_status = 'pass'",
                    connection,
                ).iloc[0]["n"]
            ),
            "zone_assignments": int(
                pd.read_sql_query(
                    "SELECT COUNT(*) AS n FROM stations WHERE lake_zone <> ''",
                    connection,
                ).iloc[0]["n"]
            ),
        }
    panel["date"] = pd.to_datetime(panel["date"])
    return panel, counts


def fit_gap_filled_models(
    model_frame: pd.DataFrame, seed: int
) -> tuple[pd.DataFrame, dict[str, object], pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    train = model_frame.loc[model_frame["split"].eq("train")]
    validation = model_frame.loc[model_frame["split"].eq("validation")]
    test = model_frame.loc[model_frame["split"].eq("test")]
    if train.empty or validation.empty or test.empty:
        raise RuntimeError("Chronological split produced an empty partition.")

    x_train = train[FEATURES]
    x_validation = validation[FEATURES]
    x_test = test[FEATURES]

    metrics_rows: list[dict[str, object]] = []
    models: dict[str, object] = {}
    prediction_frames: dict[tuple[int, str], pd.DataFrame] = {}

    for horizon in HORIZONS:
        target = f"y_{horizon}h"
        y_train = train[target].astype(int)
        y_validation = validation[target].astype(int)
        y_test = test[target].astype(int)
        if y_train.nunique() < 2 or y_validation.nunique() < 2 or y_test.nunique() < 2:
            raise RuntimeError(
                f"{target} does not contain both classes in a split; "
                "adjust the synthetic event schedule."
            )

        model = RandomForestClassifier(
            n_estimators=300,
            max_depth=6,
            min_samples_leaf=5,
            class_weight="balanced_subsample",
            random_state=seed,
            n_jobs=-1,
        )
        model.fit(x_train, y_train)
        models[f"random_forest_{horizon}h"] = model
        joblib.dump(model, MODEL_DIR / f"random_forest_{horizon}h.joblib")

        for split_name, x_split, y_split in (
            ("train", x_train, y_train),
            ("validation", x_validation, y_validation),
            ("test", x_test, y_test),
        ):
            probabilities = model.predict_proba(x_split)[:, 1]
            row = score_predictions(y_split.to_numpy(), probabilities)
            row.update(
                {
                    "model": "random_forest",
                    "horizon_hours": horizon,
                    "split": split_name,
                }
            )
            metrics_rows.append(row)

            if split_name in {"validation", "test"}:
                prediction = model_frame.loc[
                    x_split.index,
                    [
                        "date",
                        "station_id",
                        "station_name",
                        "gap_fill_lake_zone",
                        "split",
                        "synthetic_period_type",
                        "synthetic_event_id",
                        "synthetic_stress_id",
                        "target_event_id_24h",
                        "event_effect_applied",
                        "data_origin",
                    ],
                ].copy()
                prediction[f"y_{horizon}h"] = y_split.to_numpy()
                prediction[f"probability_{horizon}h"] = probabilities
                prediction_frames[(horizon, split_name)] = prediction

    test_predictions = prediction_frames[(24, "test")].copy()
    for horizon in (48, 72):
        test_predictions = test_predictions.merge(
            prediction_frames[(horizon, "test")][
                ["date", "station_id", f"y_{horizon}h", f"probability_{horizon}h"]
            ],
            on=["date", "station_id"],
            how="left",
            validate="one_to_one",
        )
    test_predictions["alert_24h"] = (
        test_predictions["probability_24h"] >= 0.5
    ).astype(int)

    feature_importance = pd.DataFrame(
        {
            "feature": FEATURES,
            "importance": models["random_forest_72h"].feature_importances_,
        }
    ).sort_values("importance", ascending=False, ignore_index=True)

    return (
        pd.DataFrame.from_records(metrics_rows),
        models,
        test_predictions,
        prediction_frames[(24, "validation")].copy(),
        feature_importance,
    )


def event_detection(
    test_predictions: pd.DataFrame, incident_reports: pd.DataFrame
) -> pd.DataFrame:
    event_lookup = {
        str(row.event_id): row
        for row in incident_reports.loc[
            incident_reports["reported_fish_kill"].eq(1)
        ].itertuples(index=False)
    }
    positives = test_predictions.loc[
        test_predictions["target_event_id_24h"].ne("")
    ].copy()
    rows: list[dict[str, object]] = []
    for event_id, group in positives.groupby("target_event_id_24h", sort=True):
        event = event_lookup.get(str(event_id))
        if event is None:
            continue
        alerts = int(group["alert_24h"].sum())
        rows.append(
            {
                "event_id": str(event_id),
                "event_start_date": str(event.start_date),
                "affected_stations": str(event.affected_stations),
                "prediction_rows": int(len(group)),
                "alerts": alerts,
                "alerted": int(alerts > 0),
                "max_probability": round(float(group["probability_24h"].max()), 6),
                "data_origin": DATA_ORIGIN,
            }
        )
    return pd.DataFrame.from_records(rows)


def write_report(
    path: Path,
    counts: dict[str, int],
    metrics: pd.DataFrame,
    events: pd.DataFrame,
    feature_importance: pd.DataFrame,
    generated_at: str,
) -> None:
    test_rf = metrics.loc[
        metrics["split"].eq("test") & metrics["model"].eq("random_forest")
    ].sort_values("horizon_hours")
    event_lines = "\n".join(
        f"| {row.event_id} | {row.event_start_date} | {row.prediction_rows} | "
        f"{row.alerts} | {row.alerted} | {row.max_probability:.3f} |"
        for row in events.itertuples(index=False)
    )
    top_features = "\n".join(
        f"| {row.feature} | {row.importance:.4f} |"
        for row in feature_importance.head(8).itertuples(index=False)
    )
    metric_lines = "\n".join(
        f"| {row.horizon_hours} | {row.n_positive} | {row.n_negative} | "
        f"{row.precision:.3f} | {row.recall:.3f} | {row.f1:.3f} | "
        f"{row.pr_auc:.3f} | {row.roc_auc:.3f} | {row.brier:.4f} | "
        f"{row.tp} | {row.fp} | {row.fn} | {row.tn} |"
        for row in test_rf.itertuples(index=False)
    )
    text = f"""# Synthetic gap-filled model report

**Generated (UTC):** {generated_at}  
**Code:** `sandbox/synthetic/train_gap_filled_model.py`  
**Database:** `data/synthetic/gap_fill/himpil_synthetic_complete.sqlite`  
**Model card:** `reports/tables/synthetic_gap_filled_model_card.md`  
**Scope:** synthetic training demonstration

## 1. What was trained

- **Input table:** `modeling_dataset` in the gap-filled SQLite database.
- **Coverage:** {counts['stations']} stations, 2016-2025, 54,795 station-days.
- **Events:** {counts['incident_reports']} exact-dated synthetic fish-kill events across 10 years.
- **Pre-event evidence:** {counts['pre_event_rows']:,} dated rows before the events.
- **Non-event windows:** {counts['negative_windows']:,} synthetic monthly patrol windows.
- **Corroboration:** {counts['corroboration_records']} independent synthetic source records.
- **Coordinates and zones:** {counts['stations']} coordinates and {counts['zone_assignments']} zone assignments.
- **Readiness:** {counts['readiness_passed']}/{counts['readiness_checks']} checks pass in the synthetic scope.
- **Targets:** event start within 24, 48, or 72 hours at the same station.
- **Split:** chronological. Train before 2023; validation 2023; test 2024-2025.
- **Model:** random forest, 300 trees, max depth 6, minimum leaf 5.

## 2. Test results

| Horizon (h) | Pos | Neg | Precision | Recall | F1 | PR-AUC | ROC-AUC | Brier | TP | FP | FN | TN |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
{metric_lines}

## 3. Event-level detection (24-hour model, test)

| Event | Start | Prediction rows | Alerts | Alerted any | Max probability |
|---|---|---:|---:|---:|---:|
{event_lines}

## 4. Top features (72-hour model)

| Feature | Importance |
|---|---:|
{top_features}

## 5. What this demonstrates

The pipeline can load a complete synthetic database, build chronological
splits, train 24/48/72-hour models, evaluate rare-event metrics, detect
events, and save artifacts. The database fills the structural gaps that block
the real pipeline, so this is an end-to-end exercise of the training system.

## 6. Boundary

The values, event dates, incident reports, corroboration, coordinates, zones,
and non-event windows are synthetic. The real evidence gate remains
{counts['real_gate_passed']} pass and {counts['real_gate_failed']} fail, and the
real dashboard still reports **risk assessment unavailable**. This model is a
demonstration, not a real Laguna de Bay advisory.

## 7. Files

- `models/synthetic/gap_filled/random_forest_24h.joblib`
- `models/synthetic/gap_filled/random_forest_48h.joblib`
- `models/synthetic/gap_filled/random_forest_72h.joblib`
- `reports/tables/synthetic_gap_filled_model_metrics.csv`
- `reports/tables/synthetic_gap_filled_test_predictions.csv`
- `reports/tables/synthetic_gap_filled_event_detection.csv`
- `reports/tables/synthetic_gap_filled_feature_importance.csv`
- `dashboard/src/data/syntheticDemo.json`
"""
    path.write_text(text, encoding="utf-8")


def write_model_card(
    path: Path,
    counts: dict[str, int],
    metrics: pd.DataFrame,
    generated_at: str,
) -> None:
    test_rf = metrics.loc[
        metrics["split"].eq("test") & metrics["model"].eq("random_forest")
    ].sort_values("horizon_hours")
    rows = "\n".join(
        f"| {row.horizon_hours} | {row.n_positive} | {row.precision:.3f} | "
        f"{row.recall:.3f} | {row.f1:.3f} | {row.pr_auc:.3f} | {row.roc_auc:.3f} | "
        f"{row.brier:.4f} |"
        for row in test_rf.itertuples(index=False)
    )
    text = f"""# Synthetic gap-filled model card

**Generated (UTC):** {generated_at}  
**Status:** synthetic gap-fill demonstration  
**Data origin:** `{DATA_ORIGIN}`

## Model details

- **Name:** HIMPIL synthetic gap-filled random forest.
- **Artifacts:** `models/synthetic/gap_filled/`.
- **Data:** `data/synthetic/gap_fill/himpil_synthetic_complete.sqlite`.
- **Seed:** `{DEFAULT_SEED}`.
- **Targets:** synthetic event start within 24, 48, or 72 hours at the same station.
- **Readiness:** {counts['readiness_passed']}/{counts['readiness_checks']} synthetic checks pass.

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
{rows}

The event effect is injected into the same variables used as features, so these
scores are optimistic by construction. The real evidence gate remains
{counts['real_gate_passed']} pass and {counts['real_gate_failed']} fail.

## Maintenance

Regenerate with:

```powershell
.\\.venv\\Scripts\\python.exe sandbox\\synthetic\\build_gap_filled_database.py
.\\.venv\\Scripts\\python.exe sandbox\\synthetic\\train_gap_filled_model.py
```
"""
    path.write_text(text, encoding="utf-8")


def write_readme(path: Path) -> None:
    text = f"""# Synthetic gap-filled model artifacts

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
.\\.venv\\Scripts\\python.exe sandbox\\synthetic\\build_gap_filled_database.py
.\\.venv\\Scripts\\python.exe sandbox\\synthetic\\train_gap_filled_model.py
```
"""
    path.write_text(text, encoding="utf-8")


def build_dashboard_payload(
    counts: dict[str, int],
    metrics: pd.DataFrame,
    events: pd.DataFrame,
    generated_at: str,
    seed: int,
    panel_rows: int,
    eligible_rows: int,
) -> dict[str, object]:
    base_manifest = json.loads(BASE_MANIFEST.read_text(encoding="utf-8"))
    real_gate = pd.read_csv(REAL_GATE)
    real_passed = int(real_gate["status"].eq("pass").sum())
    real_failed = int(real_gate["status"].eq("fail").sum())
    dashboard = json.loads(REAL_DASHBOARD.read_text(encoding="utf-8"))
    risk = dashboard.get("risk", {})

    test_rows = metrics.loc[
        metrics["split"].eq("test") & metrics["model"].eq("random_forest")
    ].sort_values("horizon_hours")
    all_metrics = [
        {
            "horizonHours": int(row.horizon_hours),
            "testRows": int(row.n_rows),
            "testPositives": int(row.n_positive),
            "precision": float(row.precision),
            "recall": float(row.recall),
            "f1": float(row.f1),
            "prAuc": float(row.pr_auc),
            "rocAuc": float(row.roc_auc),
            "brier": float(row.brier),
            "truePositives": int(row.tp),
            "falsePositives": int(row.fp),
            "falseNegatives": int(row.fn),
            "trueNegatives": int(row.tn),
        }
        for row in test_rows.itertuples(index=False)
    ]
    metric_72 = next(item for item in all_metrics if item["horizonHours"] == 72)
    detected = int(events["alerted"].sum()) if len(events) else 0
    total_events = int(len(events))
    calibration = base_manifest.get("calibration", {})

    return {
        "status": "synthetic_gap_fill_only",
        "title": "Gap-filled synthetic training run",
        "badge": "Synthetic gap-fill",
        "summary": (
            "A 72-hour random forest trained on a synthetic gap-filled database "
            "built from the supplied annual water-quality and monthly weather "
            "summaries. The database supplies dated observations, exact event "
            "dates, incident reports, non-event windows, coordinates, zone links, "
            "aggregation rules, and corroboration. The real risk state is unchanged."
        ),
        "model": "Synthetic 72-hour random forest",
        "target": (
            "Synthetic fish-kill event start within 72 hours at the same station"
        ),
        "modelPath": "models/synthetic/gap_filled/random_forest_72h.joblib",
        "databasePath": "data/synthetic/gap_fill/himpil_synthetic_complete.sqlite",
        "datasetPath": (
            "data/synthetic/gap_fill/himpil_synthetic_complete.sqlite "
            "(modeling_dataset table)"
        ),
        "reportPath": "reports/tables/synthetic_gap_filled_model_report.md",
        "metricsPath": "reports/tables/synthetic_gap_filled_model_metrics.csv",
        "modelCardPath": "reports/tables/synthetic_gap_filled_model_card.md",
        "generatedAtUtc": generated_at,
        "training": {
            "stations": int(counts["stations"]),
            "panelRows": int(panel_rows),
            "eligibleRows": int(eligible_rows),
            "syntheticEvents": int(counts["incident_reports"]),
            "stressPeriods": int(counts["stress_reports"]),
            "realAnchors": int(base_manifest["anchors"]["real_numeric_values"]),
            "imputedAnchors": int(base_manifest["anchors"]["synthetic_imputations"]),
            "provisional2025Anchors": int(
                base_manifest["anchors"]["2025_unverified_completeness"]
            ),
            "calibrationMae": float(calibration["mean_absolute_annual_mean_error"]),
            "calibrationMaxError": float(calibration["max_absolute_annual_mean_error"]),
            "split": "Train before 2023; validation 2023; test 2024-2025",
            "seed": int(seed),
        },
        "gapFill": {
            "readinessMet": int(counts["readiness_passed"]),
            "readinessTotal": int(counts["readiness_checks"]),
            "stationsWithCoordinates": int(counts["stations"]),
            "zoneAssignments": int(counts["zone_assignments"]),
            "incidentReports": int(counts["incident_reports"]),
            "stressPatrolReports": int(counts["stress_reports"]),
            "negativeWindows": int(counts["negative_windows"]),
            "corroborationRecords": int(counts["corroboration_records"]),
            "preEventObservations": int(counts["pre_event_rows"]),
            "aggregationRules": int(counts["aggregation_rules"]),
            "eventPeriods": int(counts["incident_reports"]),
        },
        "metrics": metric_72,
        "allMetrics": all_metrics,
        "eventDetection": {
            "detected": detected,
            "total": total_events,
            "note": (
                "Synthetic test events detected from pre-event rows at the 0.5 "
                "threshold using the 24-hour model."
            ),
        },
        "realState": {
            "status": risk.get("status", "insufficient_data"),
            "label": "Risk assessment unavailable",
            "gate": f"{real_passed} pass, {real_failed} fail",
        },
    }


def main() -> None:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    TABLES.mkdir(parents=True, exist_ok=True)
    DASHBOARD_DATA.parent.mkdir(parents=True, exist_ok=True)

    panel, counts = load_dataset()
    model_frame = panel.loc[panel["model_eligible"].eq(1)].copy()
    counts["panel_rows"] = len(panel)
    counts["eligible_rows"] = len(model_frame)
    real_gate = pd.read_csv(REAL_GATE)
    counts["real_gate_passed"] = int(real_gate["status"].eq("pass").sum())
    counts["real_gate_failed"] = int(real_gate["status"].eq("fail").sum())
    counts["real_gate_checks"] = int(len(real_gate))

    metrics, _models, test_predictions, validation_predictions, feature_importance = (
        fit_gap_filled_models(model_frame, DEFAULT_SEED)
    )

    with sqlite3.connect(DATABASE) as connection:
        incidents = pd.read_sql_query(
            "SELECT * FROM incident_reports", connection
        )
        events = event_detection(test_predictions, incidents)
        metrics.to_sql("model_metrics", connection, index=False, if_exists="replace")
        events.to_sql("model_event_detection", connection, index=False, if_exists="replace")
        feature_importance.to_sql(
            "model_feature_importance", connection, index=False, if_exists="replace"
        )
        connection.execute(
            "DELETE FROM metadata WHERE key IN "
            "('model_status', 'model_path', 'model_metrics', 'model_generated_at_utc')"
        )
        connection.executemany(
            "INSERT INTO metadata(key, value) VALUES (?, ?)",
            [
                ("model_status", "trained_synthetic_gap_fill"),
                ("model_path", "models/synthetic/gap_filled/random_forest_72h.joblib"),
                (
                    "model_metrics",
                    "reports/tables/synthetic_gap_filled_model_metrics.csv",
                ),
                (
                    "model_generated_at_utc",
                    datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
                ),
            ],
        )
        connection.commit()

    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    metrics_path = TABLES / "synthetic_gap_filled_model_metrics.csv"
    predictions_path = TABLES / "synthetic_gap_filled_test_predictions.csv"
    validation_path = TABLES / "synthetic_gap_filled_validation_predictions.csv"
    events_path = TABLES / "synthetic_gap_filled_event_detection.csv"
    importance_path = TABLES / "synthetic_gap_filled_feature_importance.csv"
    report_path = TABLES / "synthetic_gap_filled_model_report.md"
    card_path = TABLES / "synthetic_gap_filled_model_card.md"

    metrics.to_csv(metrics_path, index=False, encoding="utf-8-sig")
    test_predictions.to_csv(predictions_path, index=False, encoding="utf-8-sig")
    validation_predictions.to_csv(validation_path, index=False, encoding="utf-8-sig")
    events.to_csv(events_path, index=False, encoding="utf-8-sig")
    feature_importance.to_csv(importance_path, index=False, encoding="utf-8-sig")

    write_report(
        report_path, counts, metrics, events, feature_importance, generated_at
    )
    write_model_card(card_path, counts, metrics, generated_at)
    write_readme(MODEL_DIR / "README.md")

    payload = build_dashboard_payload(
        counts,
        metrics,
        events,
        generated_at,
        DEFAULT_SEED,
        len(panel),
        len(model_frame),
    )
    DASHBOARD_DATA.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    test_rf = metrics.loc[
        metrics["split"].eq("test") & metrics["model"].eq("random_forest")
    ].sort_values("horizon_hours")
    manifest = {
        "dataset": "himpil_synthetic_gap_fill_model",
        "version": "1.0",
        "status": "synthetic_gap_fill_model_only",
        "warning": WARNING,
        "data_origin": DATA_ORIGIN,
        "generated_at_utc": generated_at,
        "seed": DEFAULT_SEED,
        "source_database": _relative(DATABASE),
        "model_directory": _relative(MODEL_DIR),
        "readiness": {
            "scope": "synthetic_gap_fill",
            "checks": counts["readiness_checks"],
            "passed": counts["readiness_passed"],
        },
        "test_random_forest": [
            {
                "horizon_hours": int(row.horizon_hours),
                "n_positive": int(row.n_positive),
                "precision": float(row.precision),
                "recall": float(row.recall),
                "f1": float(row.f1),
                "pr_auc": float(row.pr_auc),
                "roc_auc": float(row.roc_auc),
                "brier": float(row.brier),
            }
            for row in test_rf.itertuples(index=False)
        ],
        "event_detection": {
            "detected": int(events["alerted"].sum()) if len(events) else 0,
            "total": int(len(events)),
        },
        "outputs": {
            "model_24h": _relative(MODEL_DIR / "random_forest_24h.joblib"),
            "model_48h": _relative(MODEL_DIR / "random_forest_48h.joblib"),
            "model_72h": _relative(MODEL_DIR / "random_forest_72h.joblib"),
            "metrics": _relative(metrics_path),
            "predictions": _relative(predictions_path),
            "event_detection": _relative(events_path),
            "feature_importance": _relative(importance_path),
            "report": _relative(report_path),
            "model_card": _relative(card_path),
            "dashboard_payload": _relative(DASHBOARD_DATA),
        },
        "quarantine": {
            "synthetic_only": True,
            "separate_from_real_evidence_bundle": True,
            "real_gate_satisfied": False,
        },
    }
    (MODEL_DIR / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    gap_manifest_path = GAP_FILL_DIR / "manifest.json"
    gap_manifest = json.loads(gap_manifest_path.read_text(encoding="utf-8"))
    gap_manifest["model_status"] = "trained_synthetic_gap_fill"
    gap_manifest["model"] = {
        "seed": DEFAULT_SEED,
        "model_24h": _relative(MODEL_DIR / "random_forest_24h.joblib"),
        "model_48h": _relative(MODEL_DIR / "random_forest_48h.joblib"),
        "model_72h": _relative(MODEL_DIR / "random_forest_72h.joblib"),
        "metrics": _relative(metrics_path),
        "report": _relative(report_path),
        "model_card": _relative(card_path),
        "dashboard_payload": _relative(DASHBOARD_DATA),
        "event_detection": manifest["event_detection"],
    }
    gap_manifest.setdefault("output_hashes_sha256", {})
    gap_manifest["output_hashes_sha256"][_relative(DATABASE)] = _sha256(DATABASE)
    for horizon in HORIZONS:
        model_path = MODEL_DIR / f"random_forest_{horizon}h.joblib"
        gap_manifest["output_hashes_sha256"][_relative(model_path)] = _sha256(model_path)
    gap_manifest_path.write_text(
        json.dumps(gap_manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print("Trained synthetic gap-filled models")
    print(f"  database: {_relative(DATABASE)}")
    print(f"  readiness: {counts['readiness_passed']}/{counts['readiness_checks']}")
    for row in test_rf.itertuples(index=False):
        print(
            f"  {int(row.horizon_hours):>2}h test: precision={row.precision:.3f} "
            f"recall={row.recall:.3f} f1={row.f1:.3f} pr_auc={row.pr_auc:.3f} "
            f"brier={row.brier:.4f}"
        )
    print(
        f"  events: {manifest['event_detection']['detected']}/"
        f"{manifest['event_detection']['total']}"
    )
    print(f"  dashboard payload: {_relative(DASHBOARD_DATA)}")


if __name__ == "__main__":
    main()
