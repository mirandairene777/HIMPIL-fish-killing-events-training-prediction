"""Train a quarantined synthetic model on the HIMPIL synthetic base dataset.

SIMULATION ONLY - NOT EVIDENCE

This script builds a *separate* synthetic event overlay on top of
``data/synthetic/base/``. It does not modify the base dataset. It injects a
known synthetic event process into a copy of the daily panel, builds only
backward-looking features, trains chronological baselines, and writes a report,
model card, metrics, predictions, and quarantined model artifacts.

The event dates, event effects, labels, probabilities, and metrics are all
simulated. They are not Laguna de Bay fish-kill evidence.

Run from the project root:
    .venv\\Scripts\\python.exe sandbox\\synthetic\\train_base_model.py
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[2]
BASE_DIR = ROOT / "data" / "synthetic" / "base"
DATA_DIR = ROOT / "data" / "synthetic" / "base_model"
MODEL_DIR = ROOT / "models" / "synthetic" / "base_model"
TABLES = ROOT / "reports" / "tables"

WARNING = "SIMULATION ONLY - NOT EVIDENCE"
DATA_ORIGIN = "synthetic_base_v1_event_overlay"
DEFAULT_SEED = 20261023
HORIZONS = (24, 48, 72)
TRAIN_END = pd.Timestamp("2023-01-01")
VALIDATION_END = pd.Timestamp("2024-01-01")

FEATURES = [
    "nitrate_mg_l",
    "phosphate_mg_l",
    "bod_mg_l",
    "ph",
    "water_temp_c",
    "do_mg_l",
    "rainfall_mm_mean",
    "wind_mps_mean",
    "air_temp_c_mean",
    "do_lag1",
    "do_lag2",
    "do_lag3",
    "do_roll3_mean",
    "do_roll7_mean",
    "do_min3",
    "do_range3",
    "do_change_1d",
    "temp_roll3_mean",
    "temp_change_1d",
    "bod_roll3_mean",
    "ph_roll3_mean",
    "rain_3d_sum",
    "rain_7d_sum",
    "wind_roll3_mean",
    "nutrient_load",
    "nutrient_roll3_mean",
]


def _relative(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _rotate_stations(index: int, count: int, offset: int) -> list[str]:
    return [
        f"LAG-LAKE-{((index * 3 + offset + step) % 15) + 1:02d}"
        for step in range(count)
    ]


def synthetic_event_schedule() -> list[dict[str, object]]:
    """Return a deterministic synthetic event/stress schedule.

    Two three-day events per year and one high-stress no-event period per year.
    The 2019 events deliberately avoid May so they are not confused with the
    single real reported May 2019 incident in the project sources.
    """
    periods: list[dict[str, object]] = []
    for index, year in enumerate(range(2016, 2026)):
        event_specs = [
            ("01", date(year, 3, 8 + (index * 3) % 17), index * 2),
            ("02", date(year, 6, 10 + (index * 5) % 17), index * 2 + 1),
        ]
        for suffix, start, sequence in event_specs:
            periods.append(
                {
                    "event_id": f"SYN-BASE-EVT-{year}-{suffix}",
                    "event_start_date": str(start),
                    "event_end_date": str(start + timedelta(days=2)),
                    "affected_stations": _rotate_stations(sequence, 5, 0),
                    "period_type": "synthetic_event",
                    "scale": 1.0,
                    "data_origin": DATA_ORIGIN,
                    "note": "Simulated event; not a real Laguna de Bay fish-kill.",
                }
            )

        stress_start = date(year, 8, 12 + (index * 2) % 10)
        periods.append(
            {
                "event_id": f"SYN-BASE-STRESS-{year}-01",
                "event_start_date": str(stress_start),
                "event_end_date": str(stress_start + timedelta(days=2)),
                "affected_stations": _rotate_stations(index * 2 + 3, 3, 5),
                "period_type": "synthetic_stress_without_event",
                "scale": 0.45,
                "data_origin": DATA_ORIGIN,
                "note": "Simulated high-stress period with no event label.",
            }
        )
    return periods


def load_base_panel() -> pd.DataFrame:
    required = [
        BASE_DIR / "water_quality_daily.csv",
        BASE_DIR / "weather_daily.csv",
        BASE_DIR / "stations.csv",
    ]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError(
            "Build the synthetic base dataset first. Missing: " + ", ".join(missing)
        )

    water = pd.read_csv(
        BASE_DIR / "water_quality_daily.csv",
        parse_dates=["date"],
        dtype={"reported_lake_zone": "string"},
        low_memory=False,
    )
    weather = pd.read_csv(BASE_DIR / "weather_daily.csv", parse_dates=["date"])
    stations = pd.read_csv(BASE_DIR / "stations.csv")

    if len(stations) != 15:
        raise ValueError(f"Expected 15 synthetic-base stations, found {len(stations)}")
    if not water["data_origin"].eq("synthetic_base_v1").all():
        raise ValueError("Base water-quality table is not marked synthetic_base_v1")

    weather_daily = (
        weather.groupby("date", as_index=False)
        .agg(
            rainfall_mm_mean=("rainfall_mm", "mean"),
            wind_mps_mean=("wind_mps", "mean"),
            air_temp_c_mean=("air_temp_c", "mean"),
        )
        .sort_values("date")
    )
    panel = water.merge(weather_daily, on="date", how="left", validate="many_to_one")
    if panel[["rainfall_mm_mean", "wind_mps_mean", "air_temp_c_mean"]].isna().any().any():
        raise AssertionError("Weather merge produced missing values")

    panel["event_effect_applied"] = 0
    panel["synthetic_period_type"] = "baseline"
    panel["synthetic_event_id"] = ""
    panel["synthetic_stress_id"] = ""
    panel["data_origin"] = DATA_ORIGIN
    return panel.sort_values(["station_id", "date"]).reset_index(drop=True)


def _apply_period(panel: pd.DataFrame, period: dict[str, object]) -> None:
    start = pd.Timestamp(str(period["event_start_date"]))
    end = pd.Timestamp(str(period["event_end_date"]))
    affected = set(str(value) for value in period["affected_stations"])
    scale = float(period["scale"])
    is_event = str(period["period_type"]) == "synthetic_event"
    window_start = start - pd.Timedelta(days=4)
    window_end = end + pd.Timedelta(days=5)

    for station_id in affected:
        station_mask = (
            panel["station_id"].eq(station_id)
            & panel["date"].ge(window_start)
            & panel["date"].le(window_end)
        )
        for index in panel.index[station_mask]:
            current = panel.at[index, "date"]
            if current < start:
                days_to_start = (start - current).days
                ramp = max(0.0, (5 - days_to_start) / 4.0)
                period_type = "pre_event" if is_event else "stress_only"
            elif current <= end:
                ramp = 1.0
                period_type = "during_event" if is_event else "stress_only"
            else:
                days_after = (current - end).days
                ramp = max(0.0, 1.0 - days_after / 4.0)
                period_type = "recovery" if is_event else "stress_only"

            panel.at[index, "do_mg_l"] = max(
                0.1, float(panel.at[index, "do_mg_l"]) - 2.7 * scale * ramp
            )
            panel.at[index, "water_temp_c"] = (
                float(panel.at[index, "water_temp_c"]) + 1.5 * scale * ramp
            )
            panel.at[index, "nitrate_mg_l"] = float(
                panel.at[index, "nitrate_mg_l"]
            ) * (1.0 + 0.55 * scale * ramp)
            panel.at[index, "phosphate_mg_l"] = float(
                panel.at[index, "phosphate_mg_l"]
            ) * (1.0 + 0.45 * scale * ramp)
            panel.at[index, "bod_mg_l"] = (
                float(panel.at[index, "bod_mg_l"]) + 1.4 * scale * ramp
            )
            panel.at[index, "ph"] = float(panel.at[index, "ph"]) - 0.08 * scale * ramp
            panel.at[index, "event_effect_applied"] = 1
            panel.at[index, "synthetic_period_type"] = period_type
            if is_event:
                panel.at[index, "synthetic_event_id"] = period["event_id"]
            else:
                panel.at[index, "synthetic_stress_id"] = period["event_id"]


def apply_synthetic_periods(
    panel: pd.DataFrame, periods: list[dict[str, object]]
) -> pd.DataFrame:
    panel = panel.copy()
    for period in periods:
        _apply_period(panel, period)
    return panel


def add_labels(panel: pd.DataFrame, periods: list[dict[str, object]]) -> pd.DataFrame:
    panel = panel.copy()
    panel["during_event"] = 0
    panel["recovery_window"] = 0
    panel["eligible_for_model"] = 1
    panel["target_event_id_24h"] = ""
    for horizon in HORIZONS:
        panel[f"y_{horizon}h"] = 0

    for event in periods:
        if str(event["period_type"]) != "synthetic_event":
            continue
        start = pd.Timestamp(str(event["event_start_date"]))
        end = pd.Timestamp(str(event["event_end_date"]))
        for station_id in event["affected_stations"]:
            station_mask = panel["station_id"].eq(station_id)
            during = station_mask & panel["date"].ge(start) & panel["date"].le(end)
            recovery = (
                station_mask
                & panel["date"].gt(end)
                & panel["date"].le(end + pd.Timedelta(days=5))
            )
            panel.loc[during, "during_event"] = 1
            panel.loc[recovery, "recovery_window"] = 1
            panel.loc[during | recovery, "eligible_for_model"] = 0

            for horizon in HORIZONS:
                for offset in range(1, horizon // 24 + 1):
                    label_date = start - pd.Timedelta(days=offset)
                    label_mask = station_mask & panel["date"].eq(label_date)
                    panel.loc[label_mask, f"y_{horizon}h"] = 1
                    if horizon == 24:
                        panel.loc[label_mask, "target_event_id_24h"] = event["event_id"]
    return panel


def add_features(panel: pd.DataFrame) -> pd.DataFrame:
    panel = panel.sort_values(["station_id", "date"]).copy()
    grouped = panel.groupby("station_id", sort=False)

    panel["do_lag1"] = grouped["do_mg_l"].shift(1)
    panel["do_lag2"] = grouped["do_mg_l"].shift(2)
    panel["do_lag3"] = grouped["do_mg_l"].shift(3)
    panel["do_roll3_mean"] = grouped["do_mg_l"].transform(
        lambda values: values.rolling(3, min_periods=1).mean()
    )
    panel["do_roll7_mean"] = grouped["do_mg_l"].transform(
        lambda values: values.rolling(7, min_periods=1).mean()
    )
    panel["do_min3"] = grouped["do_mg_l"].transform(
        lambda values: values.rolling(3, min_periods=1).min()
    )
    panel["do_range3"] = grouped["do_mg_l"].transform(
        lambda values: values.rolling(3, min_periods=1).max()
        - values.rolling(3, min_periods=1).min()
    )
    panel["do_change_1d"] = panel["do_mg_l"] - panel["do_lag1"]
    panel["temp_roll3_mean"] = grouped["water_temp_c"].transform(
        lambda values: values.rolling(3, min_periods=1).mean()
    )
    panel["temp_change_1d"] = grouped["water_temp_c"].diff()
    panel["bod_roll3_mean"] = grouped["bod_mg_l"].transform(
        lambda values: values.rolling(3, min_periods=1).mean()
    )
    panel["ph_roll3_mean"] = grouped["ph"].transform(
        lambda values: values.rolling(3, min_periods=1).mean()
    )
    panel["rain_3d_sum"] = grouped["rainfall_mm_mean"].transform(
        lambda values: values.rolling(3, min_periods=1).sum()
    )
    panel["rain_7d_sum"] = grouped["rainfall_mm_mean"].transform(
        lambda values: values.rolling(7, min_periods=1).sum()
    )
    panel["wind_roll3_mean"] = grouped["wind_mps_mean"].transform(
        lambda values: values.rolling(3, min_periods=1).mean()
    )
    panel["nutrient_load"] = (panel["nitrate_mg_l"] + panel["phosphate_mg_l"]) / 2.0
    panel["nutrient_roll3_mean"] = grouped["nutrient_load"].transform(
        lambda values: values.rolling(3, min_periods=1).mean()
    )

    panel["split"] = np.select(
        [panel["date"] < TRAIN_END, panel["date"] < VALIDATION_END],
        ["train", "validation"],
        default="test",
    )
    panel["model_eligible"] = (
        panel["eligible_for_model"].eq(1)
        & panel[FEATURES].notna().all(axis=1)
    ).astype(int)
    return panel


def build_dataset(seed: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    periods = synthetic_event_schedule()
    panel = load_base_panel()
    panel = apply_synthetic_periods(panel, periods)
    panel = add_labels(panel, periods)
    panel = add_features(panel)
    events = pd.DataFrame(periods)
    events["affected_stations"] = events["affected_stations"].map(
        lambda values: ";".join(values)
    )
    return panel, events


def _safe_metric(function, *args, **kwargs) -> float:
    try:
        return float(function(*args, **kwargs))
    except ValueError:
        return float("nan")


def score_predictions(
    y_true: np.ndarray,
    probabilities: np.ndarray,
    threshold: float = 0.5,
) -> dict[str, object]:
    predictions = (probabilities >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, predictions, labels=[0, 1]).ravel()
    return {
        "n_rows": int(len(y_true)),
        "n_positive": int(y_true.sum()),
        "n_negative": int(len(y_true) - y_true.sum()),
        "accuracy": _safe_metric(accuracy_score, y_true, predictions),
        "precision": _safe_metric(
            precision_score, y_true, predictions, zero_division=0
        ),
        "recall": _safe_metric(recall_score, y_true, predictions, zero_division=0),
        "f1": _safe_metric(f1_score, y_true, predictions, zero_division=0),
        "roc_auc": _safe_metric(roc_auc_score, y_true, probabilities),
        "pr_auc": _safe_metric(average_precision_score, y_true, probabilities),
        "brier": _safe_metric(brier_score_loss, y_true, probabilities),
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
        "threshold": float(threshold),
    }


def fit_models(
    model_frame: pd.DataFrame, seed: int
) -> tuple[pd.DataFrame, dict[str, object], pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    metrics_rows: list[dict[str, object]] = []
    models: dict[str, object] = {}
    prediction_frames: dict[tuple[int, str], pd.DataFrame] = {}

    train = model_frame.loc[model_frame["split"].eq("train")]
    validation = model_frame.loc[model_frame["split"].eq("validation")]
    test = model_frame.loc[model_frame["split"].eq("test")]
    if train.empty or validation.empty or test.empty:
        raise RuntimeError("Chronological split produced an empty partition.")

    x_train = train[FEATURES]
    x_validation = validation[FEATURES]
    x_test = test[FEATURES]

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
                        "reported_lake_zone",
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

        if horizon == 24:
            dummy = DummyClassifier(strategy="prior", random_state=seed)
            dummy.fit(x_train, y_train)
            models["dummy_24h"] = dummy
            joblib.dump(dummy, MODEL_DIR / "dummy_24h.joblib")
            dummy_probabilities = dummy.predict_proba(x_test)[:, 1]
            dummy_row = score_predictions(y_test.to_numpy(), dummy_probabilities)
            dummy_row.update(
                {"model": "dummy_prior", "horizon_hours": 24, "split": "test"}
            )
            metrics_rows.append(dummy_row)

            logistic = Pipeline(
                steps=[
                    ("imputer", SimpleImputer(strategy="median")),
                    ("scaler", StandardScaler()),
                    (
                        "classifier",
                        LogisticRegression(
                            max_iter=3000,
                            class_weight="balanced",
                            random_state=seed,
                        ),
                    ),
                ]
            )
            logistic.fit(x_train, y_train)
            models["logistic_24h"] = logistic
            joblib.dump(logistic, MODEL_DIR / "logistic_24h.joblib")
            logistic_probabilities = logistic.predict_proba(x_test)[:, 1]
            logistic_row = score_predictions(y_test.to_numpy(), logistic_probabilities)
            logistic_row.update(
                {
                    "model": "logistic_regression",
                    "horizon_hours": 24,
                    "split": "test",
                }
            )
            metrics_rows.append(logistic_row)

    test_predictions = prediction_frames[(24, "test")].copy()
    for horizon in (48, 72):
        test_predictions = test_predictions.merge(
            prediction_frames[(horizon, "test")][
                ["date", "station_id", f"y_{horizon}h", f"probability_{horizon}h"]
            ],
            on=["date", "station_id"],
            how="left",
        )
    test_predictions["alert_24h"] = (
        test_predictions["probability_24h"] >= 0.5
    ).astype(int)

    feature_importance = pd.DataFrame(
        {
            "feature": FEATURES,
            "importance": models["random_forest_24h"].feature_importances_,
        }
    ).sort_values("importance", ascending=False)

    validation_predictions = prediction_frames[(24, "validation")].copy()
    validation_predictions["alert_24h"] = (
        validation_predictions["probability_24h"] >= 0.5
    ).astype(int)
    return (
        pd.DataFrame.from_records(metrics_rows),
        models,
        test_predictions,
        validation_predictions,
        feature_importance,
    )


def event_detection(
    test_predictions: pd.DataFrame, periods: list[dict[str, object]]
) -> pd.DataFrame:
    event_lookup = {
        str(event["event_id"]): event
        for event in periods
        if str(event["period_type"]) == "synthetic_event"
    }
    positives = test_predictions.loc[
        test_predictions["target_event_id_24h"].ne("")
    ].copy()
    rows: list[dict[str, object]] = []
    for event_id, group in positives.groupby("target_event_id_24h", sort=True):
        event = event_lookup.get(str(event_id), {})
        alerts = int(group["alert_24h"].sum())
        affected = event.get("affected_stations", "")
        if isinstance(affected, (list, tuple)):
            affected = ";".join(affected)
        rows.append(
            {
                "event_id": event_id,
                "event_start_date": event.get("event_start_date", ""),
                "affected_stations": str(affected),
                "prediction_rows": int(len(group)),
                "alerts": alerts,
                "alerted": int(alerts > 0),
                "max_probability": round(float(group["probability_24h"].max()), 6),
                "data_origin": DATA_ORIGIN,
            }
        )
    return pd.DataFrame.from_records(rows)


def error_profile(test_predictions: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for period_type, group in test_predictions.groupby(
        "synthetic_period_type", sort=True
    ):
        target = group["y_24h"].astype(int)
        alert = group["alert_24h"].astype(int)
        rows.append(
            {
                "period_type": period_type,
                "rows": int(len(group)),
                "positives": int(target.sum()),
                "alerts": int(alert.sum()),
                "true_positives": int(((target == 1) & (alert == 1)).sum()),
                "false_positives": int(((target == 0) & (alert == 1)).sum()),
                "false_negatives": int(((target == 1) & (alert == 0)).sum()),
                "max_probability": round(float(group["probability_24h"].max()), 6),
                "data_origin": DATA_ORIGIN,
            }
        )
    return pd.DataFrame.from_records(rows)


def _write_report(
    path: Path,
    panel: pd.DataFrame,
    events: pd.DataFrame,
    metrics: pd.DataFrame,
    metrics_path: Path,
    feature_importance: pd.DataFrame,
    event_table: pd.DataFrame,
    diagnostics: pd.DataFrame,
    generated_at: str,
) -> None:
    test = metrics.loc[metrics["split"].eq("test")].copy()
    validation = metrics.loc[
        metrics["split"].eq("validation")
        & metrics["model"].eq("random_forest")
    ].copy()
    test_rf = test.loc[test["model"].eq("random_forest")].sort_values("horizon_hours")
    test_all = test.sort_values(["horizon_hours", "model"])
    total_events = int(events["period_type"].eq("synthetic_event").sum())
    stress_events = int(
        events["period_type"].eq("synthetic_stress_without_event").sum()
    )
    test_events = int(
        (
            events["period_type"].eq("synthetic_event")
            & events["event_start_date"].ge("2024-01-01")
        ).sum()
    )
    split_counts = panel.groupby("split").size().to_dict()
    eligible_counts = (
        panel.loc[panel["model_eligible"].eq(1)].groupby("split").size().to_dict()
    )
    positive_counts = {
        f"y_{horizon}h": int(
            panel.loc[panel["model_eligible"].eq(1), f"y_{horizon}h"].sum()
        )
        for horizon in HORIZONS
    }

    def split_positive(split_name: str, horizon: int) -> int:
        subset = panel.loc[
            panel["model_eligible"].eq(1) & panel["split"].eq(split_name)
        ]
        return int(subset[f"y_{horizon}h"].sum())

    def metric_table(frame: pd.DataFrame) -> str:
        lines = [
            "| Model | Horizon (h) | Pos | Neg | Precision | Recall | F1 | PR-AUC | ROC-AUC | Brier | TP | FP | FN | TN |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
        for row in frame.itertuples(index=False):
            lines.append(
                f"| {row.model} | {row.horizon_hours} | {row.n_positive} | {row.n_negative} | "
                f"{row.precision:.3f} | {row.recall:.3f} | {row.f1:.3f} | "
                f"{row.pr_auc:.3f} | {row.roc_auc:.3f} | {row.brier:.4f} | "
                f"{row.tp} | {row.fp} | {row.fn} | {row.tn} |"
            )
        return "\n".join(lines)

    top_features = "\n".join(
        f"| {row.feature} | {row.importance:.4f} |"
        for row in feature_importance.head(12).itertuples(index=False)
    )
    event_lines = "\n".join(
        f"| {row.event_id} | {row.event_start_date} | {row.prediction_rows} | "
        f"{row.alerts} | {row.alerted} | {row.max_probability:.3f} |"
        for row in event_table.itertuples(index=False)
    )
    diagnostic_lines = "\n".join(
        f"| {row.period_type} | {row.rows:,} | {row.positives} | {row.alerts} | "
        f"{row.true_positives} | {row.false_positives} | {row.false_negatives} | "
        f"{row.max_probability:.3f} |"
        for row in diagnostics.itertuples(index=False)
    )

    text = f"""# Synthetic base model report

> **{WARNING}**
>
> This is a model trained on a **synthetic event overlay** applied to the
> synthetic base dataset. It is not a study of Laguna de Bay, not a real
> fish-kill model, and not a real risk assessment. The base dataset is unchanged;
> the event effects and labels exist only in this separate exercise.

**Generated (UTC):** {generated_at}  
**Code:** `sandbox/synthetic/train_base_model.py`  
**Seed:** `{DEFAULT_SEED}`  
**Model card:** `reports/tables/synthetic_base_model_card.md`  
**Metrics:** `{_relative(metrics_path)}`

## 1. What was trained

- **Input:** `data/synthetic/base/water_quality_daily.csv` and `weather_daily.csv`.
- **Station labels:** 15 real lake station labels from the supplied LLDA workbooks.
- **Calendar:** 2016-01-01 to 2025-12-31; all daily values are synthetic.
- **Event overlay:** {total_events} synthetic event periods and {stress_events}
  stress-only/no-event periods. Event dates are generated, not historical.
- **Event effect:** a four-day pre-event ramp, a three-day event, and a five-day
  recovery. Affected stations receive lower DO, higher temperature, higher
  nutrients, higher BOD, and slightly lower pH.
- **Targets:** event start within 24, 48, or 72 hours at the same station.
- **Features:** current conditions, backward-looking lags, rolling means, and
  rolling rainfall/wind/nutrient summaries. No future values are used.
- **Split:** chronological. Train < 2023-01-01, validation = 2023, test >= 2024-01-01.
- **Models:** majority-class baseline, logistic regression, and random forest.

## 2. Data and split counts

| Partition | All rows | Model-eligible rows | Positive 24h | Positive 48h | Positive 72h |
|---|---:|---:|---:|---:|---:|
| train | {split_counts.get('train', 0):,} | {eligible_counts.get('train', 0):,} | {split_positive('train', 24):,} | {split_positive('train', 48):,} | {split_positive('train', 72):,} |
| validation | {split_counts.get('validation', 0):,} | {eligible_counts.get('validation', 0):,} | {split_positive('validation', 24):,} | {split_positive('validation', 48):,} | {split_positive('validation', 72):,} |
| test | {split_counts.get('test', 0):,} | {eligible_counts.get('test', 0):,} | {split_positive('test', 24):,} | {split_positive('test', 48):,} | {split_positive('test', 72):,} |
| all eligible | {int(panel['model_eligible'].sum()):,} | {int(panel['model_eligible'].sum()):,} | {positive_counts['y_24h']:,} | {positive_counts['y_48h']:,} | {positive_counts['y_72h']:,} |

Rows during an event and the five-day recovery window are excluded from fitting
and evaluation. Stress-only periods remain eligible, so false alarms are visible.

## 3. Test results (simulation only)

### Random forest

{metric_table(test_rf)}

### All test models

{metric_table(test_all)}

### Validation — random forest

{metric_table(validation)}

The test partition contains **{test_events} synthetic event periods**. That is
too few for a defensible real-world evaluation. The scores are an artifact of
injecting a strong event signature into the same variables the model sees; they
are not evidence that real fish kills are predictable.

### 24-hour error profile by period type

| Period type | Rows | Positives | Alerts | TP | FP | FN | Max probability |
|---|---:|---:|---:|---:|---:|---:|---:|
{diagnostic_lines}

The 24-hour false positives are mostly **pre-event rows 2–3 days before a
synthetic event**, not random baseline rows. The 24-hour target counts those
early warnings as false positives because the event is not within the next 24
hours. This is a **label-timing problem** for any future real model: a single
24-hour label does not credit an early warning that arrives too soon. The real
evaluation must use a lead-time policy that matches the intended advisory.

## 4. Event-level detection (24-hour model, test)

| Event | Start | Prediction rows | Alerts | Alerted any | Max probability |
|---|---|---:|---:|---:|---:|
{event_lines}

## 5. Top random-forest features (24-hour model)

| Feature | Importance |
|---|---:|
{top_features}

Feature importance describes this simulation only. It does not identify a real
cause of fish kills and must not be used as an ecological finding.

## 6. What this demonstrates

- The pipeline can join the synthetic base panel to weather.
- The pipeline can inject a known event process and build labels.
- The pipeline can construct backward-looking features without future leakage.
- The pipeline can split chronologically and evaluate rare-event metrics.
- The code can save quarantined model artifacts and a model card.
- The output can be audited against the synthetic event schedule.

## 7. What this does not demonstrate

- That Laguna de Bay fish kills are predictable.
- That any real station/zone has a risk level.
- That the synthetic event effect is realistic.
- That the event overlay preserves the base dataset's annual calibration; it does not.
- That the synthetic feature importances are ecological findings.
- That the metrics will transfer to real data.
- That the Section 6 model-readiness gate has passed.

## 8. Quarantine

- Data: `data/synthetic/base_model/` only.
- Models: `models/synthetic/base_model/` only.
- Every row has `data_origin = {DATA_ORIGIN}`.
- No synthetic row is loaded into `dashboard/src/data/dashboard.json`.
- `models/model.joblib` remains absent.
- The real dashboard must continue to show **risk assessment unavailable**.

## 9. Files

- `data/synthetic/base_model/synthetic_events.csv`
- `data/synthetic/base_model/synthetic_modeling_dataset.csv`
- `data/synthetic/base_model/synthetic_test_predictions.csv`
- `data/synthetic/base_model/manifest.json`
- `models/synthetic/base_model/*.joblib`
- `reports/tables/synthetic_base_model_metrics.csv`
- `reports/tables/synthetic_base_model_predictions.csv`
- `reports/tables/synthetic_base_model_feature_importance.csv`
- `reports/tables/synthetic_base_event_detection.csv`
- `reports/tables/synthetic_base_model_diagnostics.csv`
- `reports/tables/synthetic_base_model_card.md`
- `reports/tables/system_gaps_and_todo.md`
"""
    path.write_text(text, encoding="utf-8")


def _write_model_card(
    path: Path,
    metrics: pd.DataFrame,
    feature_importance: pd.DataFrame,
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
    top = ", ".join(feature_importance.head(5)["feature"].tolist())
    text = f"""# Synthetic base model card

> **{WARNING}**

## Model details

- **Name:** HIMPIL synthetic base model demonstration.
- **Version:** 1.0.
- **Generated (UTC):** {generated_at}.
- **Code:** `sandbox/synthetic/train_base_model.py`.
- **Artifacts:** `models/synthetic/base_model/`.
- **Data:** `data/synthetic/base/` plus a separate synthetic event overlay.
- **Seed:** `{DEFAULT_SEED}`.

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
{rows}

Top five features by random-forest importance: {top}.

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
.\\.venv\\Scripts\\python.exe sandbox\\synthetic\\build_base_dataset.py
.\\.venv\\Scripts\\python.exe sandbox\\synthetic\\train_base_model.py
```

Any change to the event schedule, features, split, or threshold requires a new
version and a new report.
"""
    path.write_text(text, encoding="utf-8")


def _write_data_readme(path: Path) -> None:
    text = f"""# Synthetic base model data

> **{WARNING}**

This folder contains the **event-overlay** data used by
`sandbox/synthetic/train_base_model.py`. It is derived from
`data/synthetic/base/`, but it is a separate synthetic modelling exercise.

| File | Description |
|---|---|
| `synthetic_events.csv` | Synthetic event and stress-only schedule. |
| `synthetic_modeling_dataset.csv` | Event-overlay panel, features, labels, split, and eligibility flags. Every row is marked `{DATA_ORIGIN}`. |
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
"""
    path.write_text(text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Train a quarantined synthetic model on the HIMPIL base dataset."
    )
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    args = parser.parse_args()
    seed = int(args.seed)

    for directory in (DATA_DIR, MODEL_DIR, TABLES):
        directory.mkdir(parents=True, exist_ok=True)

    panel, events = build_dataset(seed)
    model_frame = panel.loc[panel["model_eligible"].eq(1)].copy()
    metrics, _models, test_predictions, validation_predictions, feature_importance = (
        fit_models(model_frame, seed)
    )
    event_table = event_detection(test_predictions, events.to_dict("records"))
    diagnostics = error_profile(test_predictions)

    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    events_path = DATA_DIR / "synthetic_events.csv"
    panel_path = DATA_DIR / "synthetic_modeling_dataset.csv"
    predictions_path = DATA_DIR / "synthetic_test_predictions.csv"
    manifest_path = DATA_DIR / "manifest.json"
    metrics_path = TABLES / "synthetic_base_model_metrics.csv"
    report_predictions_path = TABLES / "synthetic_base_model_predictions.csv"
    importance_path = TABLES / "synthetic_base_model_feature_importance.csv"
    detection_path = TABLES / "synthetic_base_event_detection.csv"
    diagnostics_path = TABLES / "synthetic_base_model_diagnostics.csv"
    report_path = TABLES / "synthetic_base_model_report.md"
    card_path = TABLES / "synthetic_base_model_card.md"

    events.to_csv(events_path, index=False, encoding="utf-8-sig")
    panel.to_csv(panel_path, index=False, encoding="utf-8-sig")
    test_predictions.to_csv(predictions_path, index=False, encoding="utf-8-sig")
    metrics.to_csv(metrics_path, index=False, encoding="utf-8-sig")
    test_predictions.to_csv(report_predictions_path, index=False, encoding="utf-8-sig")
    feature_importance.to_csv(importance_path, index=False, encoding="utf-8-sig")
    event_table.to_csv(detection_path, index=False, encoding="utf-8-sig")
    diagnostics.to_csv(diagnostics_path, index=False, encoding="utf-8-sig")

    _write_data_readme(DATA_DIR / "README.md")
    _write_report(
        report_path,
        panel,
        events,
        metrics,
        metrics_path,
        feature_importance,
        event_table,
        diagnostics,
        generated_at,
    )
    _write_model_card(card_path, metrics, feature_importance, generated_at)

    test_rf = metrics.loc[
        metrics["split"].eq("test") & metrics["model"].eq("random_forest")
    ]
    manifest = {
        "dataset": "himpil_synthetic_base_model",
        "version": "1.0",
        "status": "synthetic_model_only",
        "warning": WARNING,
        "data_origin": DATA_ORIGIN,
        "generated_at_utc": generated_at,
        "seed": seed,
        "source_dataset": _relative(BASE_DIR),
        "source_hashes_sha256": {
            _relative(BASE_DIR / "water_quality_daily.csv"): _sha256(
                BASE_DIR / "water_quality_daily.csv"
            ),
            _relative(BASE_DIR / "weather_daily.csv"): _sha256(
                BASE_DIR / "weather_daily.csv"
            ),
            _relative(BASE_DIR / "stations.csv"): _sha256(
                BASE_DIR / "stations.csv"
            ),
        },
        "coverage": {
            "rows": int(len(panel)),
            "stations": int(panel["station_id"].nunique()),
            "start_date": str(panel["date"].min().date()),
            "end_date": str(panel["date"].max().date()),
            "synthetic_event_periods": int(
                events["period_type"].eq("synthetic_event").sum()
            ),
            "synthetic_stress_periods": int(
                events["period_type"].eq("synthetic_stress_without_event").sum()
            ),
            "model_eligible_rows": int(model_frame.shape[0]),
        },
        "features": FEATURES,
        "split": {
            "train": "2016-01-01 to 2022-12-31",
            "validation": "2023-01-01 to 2023-12-31",
            "test": "2024-01-01 to 2025-12-31",
        },
        "test_random_forest": test_rf[
            ["horizon_hours", "n_positive", "precision", "recall", "f1", "pr_auc", "roc_auc", "brier"]
        ].to_dict("records"),
        "test_24h_error_profile": diagnostics.to_dict("records"),
        "quarantine": {
            "not_evidence": True,
            "does_not_satisfy_model_gate": True,
            "not_connected_to_dashboard": True,
            "contains_real_station_labels": True,
            "contains_real_annual_anchors": False,
            "derived_from_dataset_with_real_annual_anchors": True,
            "contains_real_daily_measurements": False,
            "contains_synthetic_event_labels": True,
            "contains_real_event_dates": False,
        },
        "limitations": [
            "Event dates and effects are synthetic.",
            "Labels are generated from the synthetic event schedule.",
            "Metrics are optimistic because the event effect is in the features.",
            "No real daily observations or verified fish-kill events are used.",
            "No station coordinates or authoritative station-to-zone crosswalk.",
        ],
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(WARNING)
    print(f"Wrote synthetic base-model artifacts to {DATA_DIR}")
    print(f"  panel rows: {len(panel):,}")
    print(f"  model-eligible rows: {len(model_frame):,}")
    print(f"  synthetic events: {int(events['period_type'].eq('synthetic_event').sum())}")
    print(f"  stress-only periods: {int(events['period_type'].eq('synthetic_stress_without_event').sum())}")
    print("  test random forest:")
    for row in test_rf.sort_values("horizon_hours").itertuples(index=False):
        print(
            f"    {row.horizon_hours}h: positives={row.n_positive}, "
            f"precision={row.precision:.3f}, recall={row.recall:.3f}, "
            f"f1={row.f1:.3f}, pr_auc={row.pr_auc:.3f}, brier={row.brier:.4f}"
        )
    print(f"  report: {_relative(report_path)}")


if __name__ == "__main__":
    main()
