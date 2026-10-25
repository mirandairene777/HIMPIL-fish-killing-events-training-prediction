"""HIMPIL quarantined synthetic prototype.

This script demonstrates the end-to-end modelling workflow on **simulated**
station-day data. It exists so the team can test the pipeline, inspect a model
card, and discuss a future dashboard design while the real-data requests are
pending.

It does not use any real Laguna de Bay observation, station, event date, zone,
or incident. It does not write to data/processed/, does not overwrite
models/model.joblib, and does not feed the evidence dashboard. Its metrics are
simulation results, not evidence about Laguna de Bay.

Run from the project root:
    .venv\\Scripts\\python.exe sandbox\\synthetic\\run_prototype.py

Outputs:
    data/synthetic/                  synthetic panel, labels, predictions, manifest
    models/synthetic/                quarantined model artifacts
    reports/tables/synthetic_*      report, model card, metrics, importances
"""

from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
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

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SYNTHETIC_DATA_DIR = PROJECT_ROOT / "data" / "synthetic"
SYNTHETIC_MODEL_DIR = PROJECT_ROOT / "models" / "synthetic"
TABLE_DIR = PROJECT_ROOT / "reports" / "tables"

DEFAULT_SEED = 20261023
HORIZONS = (24, 48, 72)
TRAIN_END = pd.Timestamp("2023-01-01")
VALIDATION_END = pd.Timestamp("2024-01-01")
SIMULATION_START = "2021-01-01"
SIMULATION_END = "2024-12-31"

STATIONS = [
    {
        "station_id": "SYN-LAG-01",
        "zone_id": "SYN-ZONE-A",
        "do_offset": -0.25,
        "temp_offset": 0.10,
        "nutrient_offset": 0.10,
    },
    {
        "station_id": "SYN-LAG-02",
        "zone_id": "SYN-ZONE-A",
        "do_offset": 0.10,
        "temp_offset": -0.05,
        "nutrient_offset": -0.05,
    },
    {
        "station_id": "SYN-LAG-03",
        "zone_id": "SYN-ZONE-B",
        "do_offset": -0.10,
        "temp_offset": 0.20,
        "nutrient_offset": 0.15,
    },
    {
        "station_id": "SYN-LAG-04",
        "zone_id": "SYN-ZONE-B",
        "do_offset": 0.20,
        "temp_offset": 0.00,
        "nutrient_offset": 0.00,
    },
    {
        "station_id": "SYN-LAG-05",
        "zone_id": "SYN-ZONE-C",
        "do_offset": 0.00,
        "temp_offset": -0.10,
        "nutrient_offset": -0.10,
    },
    {
        "station_id": "SYN-LAG-06",
        "zone_id": "SYN-ZONE-C",
        "do_offset": -0.15,
        "temp_offset": 0.15,
        "nutrient_offset": 0.05,
    },
]

# Simulated event periods. These dates are examples in a synthetic calendar;
# they are not real Laguna de Bay fish-kill dates.
EVENT_PERIODS = [
    {
        "event_id": "SYN-EVT-2021-01",
        "start": "2021-04-19",
        "end": "2021-04-21",
        "stations": ["SYN-LAG-01", "SYN-LAG-02", "SYN-LAG-03"],
    },
    {
        "event_id": "SYN-EVT-2021-02",
        "start": "2021-06-07",
        "end": "2021-06-09",
        "stations": ["SYN-LAG-02", "SYN-LAG-04"],
    },
    {
        "event_id": "SYN-EVT-2022-01",
        "start": "2022-05-09",
        "end": "2022-05-11",
        "stations": ["SYN-LAG-01", "SYN-LAG-03", "SYN-LAG-05"],
    },
    {
        "event_id": "SYN-EVT-2022-02",
        "start": "2022-06-20",
        "end": "2022-06-22",
        "stations": ["SYN-LAG-04", "SYN-LAG-06"],
    },
    {
        "event_id": "SYN-EVT-2023-01",
        "start": "2023-04-17",
        "end": "2023-04-19",
        "stations": ["SYN-LAG-02", "SYN-LAG-03", "SYN-LAG-06"],
    },
    {
        "event_id": "SYN-EVT-2023-02",
        "start": "2023-06-05",
        "end": "2023-06-07",
        "stations": ["SYN-LAG-01", "SYN-LAG-05"],
    },
    {
        "event_id": "SYN-EVT-2024-01",
        "start": "2024-05-13",
        "end": "2024-05-15",
        "stations": ["SYN-LAG-01", "SYN-LAG-04", "SYN-LAG-06"],
    },
    {
        "event_id": "SYN-EVT-2024-02",
        "start": "2024-06-24",
        "end": "2024-06-26",
        "stations": ["SYN-LAG-02", "SYN-LAG-03", "SYN-LAG-05"],
    },
]

# High-stress periods with no synthetic fish-kill label. They make the
# demonstration less trivial by creating plausible false-positive windows.
STRESS_PERIODS = [
    {
        "stress_id": "SYN-STRESS-2022-01",
        "start": "2022-04-25",
        "end": "2022-04-27",
        "stations": ["SYN-LAG-02", "SYN-LAG-05"],
    },
    {
        "stress_id": "SYN-STRESS-2023-01",
        "start": "2023-05-22",
        "end": "2023-05-24",
        "stations": ["SYN-LAG-01", "SYN-LAG-04"],
    },
    {
        "stress_id": "SYN-STRESS-2024-01",
        "start": "2024-04-29",
        "end": "2024-05-01",
        "stations": ["SYN-LAG-02", "SYN-LAG-05"],
    },
]

FEATURES = [
    "do_mg_l",
    "water_temp_c",
    "ph",
    "nitrate_mg_l",
    "phosphate_mg_l",
    "bod_mg_l",
    "rainfall_mm",
    "wind_mps",
    "air_temp_c",
    "do_lag1",
    "do_lag2",
    "do_lag3",
    "do_roll3_mean",
    "do_roll7_mean",
    "do_min3",
    "do_change_1d",
    "temp_roll3_mean",
    "rain_3d_sum",
    "rain_7d_sum",
    "wind_roll3_mean",
    "nutrient_roll3_mean",
]


def ensure_output_dirs() -> None:
    for path in (SYNTHETIC_DATA_DIR, SYNTHETIC_MODEL_DIR, TABLE_DIR):
        path.mkdir(parents=True, exist_ok=True)


def station_frame() -> pd.DataFrame:
    return pd.DataFrame(STATIONS)


def build_base_panel(seed: int) -> pd.DataFrame:
    """Generate a plausible daily station-day panel with no event effects."""
    rng = np.random.default_rng(seed)
    dates = pd.date_range(SIMULATION_START, SIMULATION_END, freq="D")
    frames: list[pd.DataFrame] = []

    for station in STATIONS:
        n = len(dates)
        day_of_year = dates.day_of_year.to_numpy(dtype=float)
        seasonal = np.sin(2 * np.pi * (day_of_year - 80) / 365.25)
        wet = 0.5 + 0.5 * np.cos(2 * np.pi * (day_of_year - 200) / 365.25)

        rain_probability = np.clip(0.04 + 0.36 * wet, 0.0, 0.65)
        rain = np.where(
            rng.random(n) < rain_probability,
            rng.gamma(shape=1.5, scale=8.0, size=n) * (0.55 + 0.65 * wet),
            0.0,
        )
        wind = np.clip(
            2.2
            + 0.5 * np.cos(2 * np.pi * (day_of_year - 20) / 365.25)
            + 0.25 * seasonal
            + rng.normal(0.0, 0.55, n),
            0.2,
            None,
        )
        water_temp = (
            27.5
            + 2.8 * seasonal
            + station["temp_offset"]
            + rng.normal(0.0, 0.35, n)
        )
        nitrate = np.exp(
            0.15
            + 0.28 * wet
            + 0.11 * np.log1p(rain)
            + station["nutrient_offset"]
            + rng.normal(0.0, 0.18, n)
        )
        phosphate = np.exp(
            -0.70
            + 0.16 * wet
            + 0.08 * np.log1p(rain)
            + 0.5 * station["nutrient_offset"]
            + rng.normal(0.0, 0.15, n)
        )
        do = (
            8.15
            - 0.30 * (water_temp - 27.5)
            + 0.18 * (wind - 2.2)
            - 0.10 * np.log1p(rain)
            - 0.20 * (nitrate - 1.0)
            + station["do_offset"]
            + rng.normal(0.0, 0.22, n)
        )
        bod = (
            1.9
            + 0.35 * wet
            + 0.25 * nitrate
            + 0.40 * phosphate
            + rng.normal(0.0, 0.25, n)
        )
        ph = (
            7.80
            + 0.08 * seasonal
            - 0.03 * (nitrate - 1.0)
            + rng.normal(0.0, 0.06, n)
        )
        air_temp = water_temp + 0.4 + rng.normal(0.0, 0.7, n)

        frame = pd.DataFrame(
            {
                "date": dates,
                "station_id": station["station_id"],
                "zone_id": station["zone_id"],
                "water_temp_c": water_temp,
                "air_temp_c": air_temp,
                "ph": ph,
                "do_mg_l": np.clip(do, 0.2, None),
                "nitrate_mg_l": nitrate,
                "phosphate_mg_l": phosphate,
                "bod_mg_l": np.clip(bod, 0.1, None),
                "rainfall_mm": rain,
                "wind_mps": wind,
                "data_origin": "synthetic_simulation",
            }
        )
        frames.append(frame)

    panel = pd.concat(frames, ignore_index=True)
    panel = panel.sort_values(["station_id", "date"]).reset_index(drop=True)
    return panel


def _period_effects(
    panel: pd.DataFrame,
    period: dict,
    scale: float,
    period_type: str,
    id_column: str,
    period_id: str,
) -> None:
    """Apply a pre-event decline, event trough, and post-event recovery."""
    start = pd.Timestamp(period["start"])
    end = pd.Timestamp(period["end"])
    affected = set(period["stations"])
    window_start = start - pd.Timedelta(days=4)
    window_end = end + pd.Timedelta(days=5)

    for station_id in affected:
        station_mask = (
            (panel["station_id"] == station_id)
            & (panel["date"] >= window_start)
            & (panel["date"] <= window_end)
        )
        for index in panel.index[station_mask]:
            current = panel.at[index, "date"]
            if current < start:
                days_to_start = (start - current).days
                ramp = max(0.0, (5 - days_to_start) / 4.0)
                current_type = "event_pre" if period_type == "event" else "stress_only"
            elif current <= end:
                ramp = 1.0
                current_type = "event_during" if period_type == "event" else "stress_only"
            else:
                days_after = (current - end).days
                ramp = max(0.0, 1.0 - days_after / 4.0)
                current_type = "event_recovery" if period_type == "event" else "stress_only"

            panel.at[index, "do_mg_l"] = max(
                0.1, panel.at[index, "do_mg_l"] - scale * 2.7 * ramp
            )
            panel.at[index, "water_temp_c"] += scale * 1.5 * ramp
            panel.at[index, "air_temp_c"] += scale * 1.1 * ramp
            panel.at[index, "nitrate_mg_l"] *= 1.0 + scale * 0.55 * ramp
            panel.at[index, "phosphate_mg_l"] *= 1.0 + scale * 0.45 * ramp
            panel.at[index, "bod_mg_l"] += scale * 1.4 * ramp
            panel.at[index, "wind_mps"] = max(
                0.1, panel.at[index, "wind_mps"] * (1.0 - scale * 0.25 * ramp)
            )
            panel.at[index, id_column] = period_id
            panel.at[index, "simulation_period_type"] = current_type


def add_simulated_periods(panel: pd.DataFrame) -> pd.DataFrame:
    panel = panel.copy()
    panel["simulation_period_type"] = "baseline"
    panel["synthetic_event_id"] = ""
    panel["synthetic_stress_id"] = ""

    for event in EVENT_PERIODS:
        _period_effects(
            panel,
            event,
            scale=1.0,
            period_type="event",
            id_column="synthetic_event_id",
            period_id=event["event_id"],
        )
    for stress in STRESS_PERIODS:
        _period_effects(
            panel,
            stress,
            scale=0.48,
            period_type="stress",
            id_column="synthetic_stress_id",
            period_id=stress["stress_id"],
        )
    return panel


def add_labels_and_eligibility(panel: pd.DataFrame) -> pd.DataFrame:
    panel = panel.copy()
    panel["during_event"] = 0
    panel["recovery_window"] = 0
    panel["eligible_for_model"] = 1
    panel["target_event_id_24h"] = ""

    for horizon in HORIZONS:
        panel[f"y_{horizon}h"] = 0

    for event in EVENT_PERIODS:
        start = pd.Timestamp(event["start"])
        end = pd.Timestamp(event["end"])
        for station_id in event["stations"]:
            station_mask = panel["station_id"] == station_id
            during = station_mask & (panel["date"] >= start) & (panel["date"] <= end)
            recovery = (
                station_mask
                & (panel["date"] > end)
                & (panel["date"] <= end + pd.Timedelta(days=5))
            )
            panel.loc[during, "during_event"] = 1
            panel.loc[recovery, "recovery_window"] = 1
            panel.loc[during | recovery, "eligible_for_model"] = 0

            for horizon in HORIZONS:
                lead_days = horizon // 24
                for offset in range(1, lead_days + 1):
                    label_date = start - pd.Timedelta(days=offset)
                    label_mask = station_mask & (panel["date"] == label_date)
                    panel.loc[label_mask, f"y_{horizon}h"] = 1
                    if horizon == 24:
                        panel.loc[label_mask, "target_event_id_24h"] = event["event_id"]

    # Stress-only periods are deliberately eligible: they are high-risk
    # non-events and should test false alarms.
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
    panel["do_change_1d"] = panel["do_mg_l"] - panel["do_lag1"]
    panel["temp_roll3_mean"] = grouped["water_temp_c"].transform(
        lambda values: values.rolling(3, min_periods=1).mean()
    )
    panel["rain_3d_sum"] = grouped["rainfall_mm"].transform(
        lambda values: values.rolling(3, min_periods=1).sum()
    )
    panel["rain_7d_sum"] = grouped["rainfall_mm"].transform(
        lambda values: values.rolling(7, min_periods=1).sum()
    )
    panel["wind_roll3_mean"] = grouped["wind_mps"].transform(
        lambda values: values.rolling(3, min_periods=1).mean()
    )
    panel["nutrient_load"] = (panel["nitrate_mg_l"] + panel["phosphate_mg_l"]) / 2
    panel["nutrient_roll3_mean"] = panel.groupby("station_id", sort=False)[
        "nutrient_load"
    ].transform(lambda values: values.rolling(3, min_periods=1).mean())

    panel["split"] = np.select(
        [panel["date"] < TRAIN_END, panel["date"] < VALIDATION_END],
        ["train", "validation"],
        default="test",
    )
    return panel


def build_synthetic_dataset(seed: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    base = build_base_panel(seed)
    with_periods = add_simulated_periods(base)
    with_features = add_features(with_periods)
    with_labels = add_labels_and_eligibility(with_features)

    events = []
    for event in EVENT_PERIODS:
        events.append(
            {
                "event_id": event["event_id"],
                "event_start_date": event["start"],
                "event_end_date": event["end"],
                "affected_stations": ";".join(event["stations"]),
                "period_type": "synthetic_event",
                "data_origin": "synthetic_simulation",
                "note": "Simulated event; not a real Laguna de Bay incident.",
            }
        )
    for stress in STRESS_PERIODS:
        events.append(
            {
                "event_id": stress["stress_id"],
                "event_start_date": stress["start"],
                "event_end_date": stress["end"],
                "affected_stations": ";".join(stress["stations"]),
                "period_type": "synthetic_stress_without_event",
                "data_origin": "synthetic_simulation",
                "note": "Simulated high-stress period with no event label.",
            }
        )
    event_frame = pd.DataFrame(events)
    return with_labels, event_frame


def _safe_metric(function, *args, **kwargs):
    try:
        return float(function(*args, **kwargs))
    except ValueError:
        return float("nan")


def score_predictions(
    y_true: np.ndarray,
    probabilities: np.ndarray,
    threshold: float = 0.5,
) -> dict:
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
) -> tuple[list[dict], dict[str, object], pd.DataFrame, pd.DataFrame]:
    metrics_rows: list[dict] = []
    models: dict[str, object] = {}
    predictions_by_horizon_split: dict[tuple[int, str], pd.DataFrame] = {}

    train = model_frame[model_frame["split"] == "train"]
    validation = model_frame[model_frame["split"] == "validation"]
    test = model_frame[model_frame["split"] == "test"]

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

        if y_train.nunique() < 2 or y_test.nunique() < 2:
            raise RuntimeError(
                f"{target} does not contain both classes in train/test; "
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
        joblib.dump(model, SYNTHETIC_MODEL_DIR / f"random_forest_{horizon}h.joblib")

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
                predictions = model_frame.loc[x_split.index, [
                    "date",
                    "station_id",
                    "zone_id",
                    "split",
                    "simulation_period_type",
                    "synthetic_event_id",
                    "target_event_id_24h",
                ]].copy()
                predictions[f"y_{horizon}h"] = y_split.to_numpy()
                predictions[f"probability_{horizon}h"] = probabilities
                predictions_by_horizon_split[(horizon, split_name)] = predictions

        if horizon == 24:
            dummy = DummyClassifier(strategy="prior", random_state=seed)
            dummy.fit(x_train, y_train)
            models["dummy_24h"] = dummy
            joblib.dump(dummy, SYNTHETIC_MODEL_DIR / "dummy_24h.joblib")
            dummy_probabilities = dummy.predict_proba(x_test)[:, 1]
            dummy_row = score_predictions(y_test.to_numpy(), dummy_probabilities)
            dummy_row.update(
                {
                    "model": "dummy_prior",
                    "horizon_hours": 24,
                    "split": "test",
                }
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
            joblib.dump(logistic, SYNTHETIC_MODEL_DIR / "logistic_24h.joblib")
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

    test_predictions = predictions_by_horizon_split[(24, "test")].copy()
    for horizon in (48, 72):
        test_predictions = test_predictions.merge(
            predictions_by_horizon_split[(horizon, "test")][
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
    return metrics_rows, models, test_predictions, feature_importance


def event_detection(test_predictions: pd.DataFrame) -> pd.DataFrame:
    positives = test_predictions[test_predictions["target_event_id_24h"] != ""].copy()
    rows = []
    for event_id, group in positives.groupby("target_event_id_24h", sort=True):
        alerts = int(group["alert_24h"].sum())
        rows.append(
            {
                "event_id": event_id,
                "pre_event_station_rows": int(len(group)),
                "alerts_at_0_5": alerts,
                "detected_at_least_once": int(alerts > 0),
                "max_probability": float(group["probability_24h"].max()),
                "data_origin": "synthetic_simulation",
            }
        )
    return pd.DataFrame(rows)


def markdown_metric_table(metrics: pd.DataFrame, split: str) -> str:
    subset = metrics[
        (metrics["split"] == split)
        & (
            ((metrics["model"] == "random_forest"))
            | (metrics["split"] == "test")
        )
    ].copy()
    subset = subset.sort_values(["horizon_hours", "model"])
    columns = [
        ("model", "Model"),
        ("horizon_hours", "Horizon (h)"),
        ("n_positive", "Positives"),
        ("n_negative", "Negatives"),
        ("precision", "Precision"),
        ("recall", "Recall"),
        ("f1", "F1"),
        ("pr_auc", "PR-AUC"),
        ("roc_auc", "ROC-AUC"),
        ("brier", "Brier"),
        ("tp", "TP"),
        ("fp", "FP"),
        ("fn", "FN"),
        ("tn", "TN"),
    ]
    lines = [
        "| " + " | ".join(label for _, label in columns) + " |",
        "|" + "|".join("---" for _ in columns) + "|",
    ]
    for _, row in subset.iterrows():
        cells = []
        for key, _ in columns:
            value = row[key]
            if isinstance(value, float):
                cells.append("" if math.isnan(value) else f"{value:.3f}")
            else:
                cells.append(str(value))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def write_report(
    panel: pd.DataFrame,
    events: pd.DataFrame,
    metrics: pd.DataFrame,
    importance: pd.DataFrame,
    detection: pd.DataFrame,
    seed: int,
    generated_at: str,
) -> None:
    train = panel[panel["split"] == "train"]
    validation = panel[panel["split"] == "validation"]
    test = panel[panel["split"] == "test"]

    event_rows = events[events["period_type"] == "synthetic_event"]
    stress_rows = events[events["period_type"] == "synthetic_stress_without_event"]

    def event_table(frame: pd.DataFrame) -> str:
        lines = [
            "| ID | Start | End | Affected synthetic stations |",
            "|---|---|---|---|",
        ]
        for _, row in frame.iterrows():
            lines.append(
                "| "
                + " | ".join(
                    [
                        str(row["event_id"]),
                        str(row["event_start_date"]),
                        str(row["event_end_date"]),
                        str(row["affected_stations"]).replace(";", ", "),
                    ]
                )
                + " |"
            )
        return "\n".join(lines)

    def split_table() -> str:
        rows = []
        for name, frame in (
            ("Train", train),
            ("Validation", validation),
            ("Test", test),
        ):
            event_count = frame.loc[
                frame["synthetic_event_id"] != "", "synthetic_event_id"
            ].nunique()
            rows.append(
                (
                    name,
                    str(frame["date"].min().date()),
                    str(frame["date"].max().date()),
                    len(frame),
                    event_count,
                )
            )
        lines = [
            "| Split | Start | End | Rows | Event periods present |",
            "|---|---|---|---:|---:|",
        ]
        for row in rows:
            lines.append("| " + " | ".join(str(value) for value in row) + " |")
        return "\n".join(lines)

    top_features = importance.head(10)
    feature_lines = [
        "| Rank | Feature | Importance (simulation) |",
        "|---:|---|---:|",
    ]
    for rank, (_, row) in enumerate(top_features.iterrows(), start=1):
        feature_lines.append(
            f"| {rank} | `{row['feature']}` | {row['importance']:.4f} |"
        )

    detection_lines = [
        "| Event | Pre-event station rows | Alerts at 0.50 | Detected at least once | Max probability |",
        "|---|---:|---:|---:|---:|",
    ]
    for _, row in detection.iterrows():
        detection_lines.append(
            "| "
            + " | ".join(
                [
                    str(row["event_id"]),
                    str(int(row["pre_event_station_rows"])),
                    str(int(row["alerts_at_0_5"])),
                    "yes" if int(row["detected_at_least_once"]) else "no",
                    f"{row['max_probability']:.3f}",
                ]
            )
            + " |"
        )

    report = f"""# HIMPIL synthetic prototype report

> **SIMULATION ONLY — NOT EVIDENCE**
>
> Every row, station, date, event, probability, and metric in this report comes
> from a synthetic data generator. This is **not** a study of Laguna de Bay, not
> a real fish-kill record, not a real risk assessment, and not a substitute for
> the Section 6 model-readiness gate. The real-data dashboard continues to show
> **risk assessment unavailable**.

**Generated (UTC):** {generated_at}  
**Random seed:** `{seed}`  
**Code:** [`sandbox/synthetic/run_prototype.py`](../../sandbox/synthetic/run_prototype.py)  
**Model card:** [`synthetic_model_card.md`](synthetic_model_card.md)  
**Guardrail:** this prototype is quarantined outside `data/processed/`, `models/model.joblib`, and the evidence dashboard.

## 1. What this prototype demonstrates

The prototype exercises the full workflow that the real study will need:

1. generate a daily station-day panel with weather and water-quality variables;
2. inject **known** simulated event periods and high-stress non-event periods;
3. build only backward-looking features and a 24/48/72-hour target;
4. split chronologically by date;
5. fit a majority-class baseline, a logistic regression, and a random forest;
6. evaluate precision, recall, F1, PR-AUC, ROC-AUC, Brier score, and a confusion matrix;
7. produce a model artifact, a model card, and an auditable report.

## 2. What it does not demonstrate

- It does **not** estimate real fish-kill risk in Laguna de Bay.
- It does **not** use real station coordinates, zones, event dates, or observations.
- It does **not** pass the Section 6 gate. The gate requires real daily observations,
  multiple verified event periods across years, credible negatives, station/zone
  mapping, a data dictionary, and leakage review.
- It does **not** justify a live warning, advisory, SMS alert, or public risk category.
- Its high or low metrics are properties of the simulation. They must never be
  quoted as HIMPIL's real-world performance.

## 3. Simulated data-generating process

- **Calendar:** {SIMULATION_START} to {SIMULATION_END}; synthetic dates only.
- **Stations:** six synthetic stations (`SYN-LAG-01` to `SYN-LAG-06`) in three
  synthetic zones (`SYN-ZONE-A`, `SYN-ZONE-B`, `SYN-ZONE-C`).
- **Weather:** seasonal rainfall, wind, and air temperature with noise.
- **Water quality:** dissolved oxygen, water temperature, pH, nitrate, phosphate,
  and BOD. The baseline includes seasonal and station-level variation.
- **Event effect:** for affected stations, DO falls and temperature, nutrients,
  BOD, and pH shift over a four-day pre-event ramp, a three-day event, and a
  five-day recovery. Event labels are generated from the known simulation
  schedule.
- **Stress-only periods:** high-stress conditions with no event label. They create
  plausible false-positive windows and make the demonstration less trivial.
- **Data-origin column:** every row is marked `synthetic_simulation`.

### Simulated event periods

{event_table(event_rows)}

### Simulated high-stress, no-event periods

{event_table(stress_rows)}

## 4. Target and split

For a row at date `t`:

- `y_24h = 1` when a simulated event starts the next day at that station.
- `y_48h = 1` when a simulated event starts within the next two days.
- `y_72h = 1` when a simulated event starts within the next three days.

Rows during an event and during the five-day recovery window are excluded from
model fitting and evaluation. Rows in stress-only periods remain eligible, so
false alarms are visible.

### Chronological partitions

{split_table()}

The split is by date, never random. A random split would leak the same simulated
event period into training and test.

## 5. Results (simulation only)

### Test partition — all models

{markdown_metric_table(metrics, "test")}

### Validation partition — random forest

{markdown_metric_table(metrics, "validation")}

The test partition contains only two simulated event periods. The positive counts
are small, so the metrics are unstable even within the simulation. This is one
reason the numbers cannot be transferred to the real setting.

### Event-level test detection at threshold 0.50

{chr(10).join(detection_lines)}

A missed event means every pre-event station row in that period stayed below
0.50. A detected event means at least one row crossed the threshold. This is a
demonstration of the evaluation code, not evidence of real warning skill.

## 6. Top random-forest features (simulation only)

{chr(10).join(feature_lines)}

Feature importance is model-specific, unstable, and computed on synthetic data.
It must not be presented as a finding about Laguna de Bay.

## 7. Reproducibility and outputs

Run:

```powershell
.\\.venv\\Scripts\\python.exe sandbox\\synthetic\\run_prototype.py
```

Outputs:

| Output | Path | Status |
|---|---|---|
| Synthetic panel | `data/synthetic/synthetic_station_day.csv` | simulation only |
| Event truth table | `data/synthetic/synthetic_event_periods.csv` | simulation only |
| Modelling table | `data/synthetic/synthetic_modeling_dataset.csv` | simulation only |
| Test predictions | `data/synthetic/synthetic_test_predictions.csv` | simulation only |
| Manifest | `data/synthetic/synthetic_manifest.json` | simulation only |
| Models | `models/synthetic/*.joblib` | quarantined |
| Metrics | `reports/tables/synthetic_prototype_metrics.csv` | simulation only |
| Feature importance | `reports/tables/synthetic_feature_importance.csv` | simulation only |
| Event detection | `reports/tables/synthetic_event_detection.csv` | simulation only |

## 8. Quarantine rules

1. Never copy these rows into `data/processed/` or the real dashboard.
2. Never call the synthetic model “the HIMPIL model” without “synthetic prototype”.
3. Never quote these metrics in a defense, abstract, or paper as real performance.
4. Never use this model to issue an advisory or risk level.
5. Remove or archive the prototype when real data and a real model replace it.

## 9. What the team should take from this

The prototype proves that the **software pipeline** can generate a panel, build
leakage-aware features, train models, evaluate rare-event metrics, and produce a
model card. It does not reduce the evidence gap. The next real milestone is still
data access: LLDA daily observations, station metadata, incident records,
reporting completeness, and an authoritative zone crosswalk.

See [`README_WORKPLAN.md`](../../README_WORKPLAN.md) Section 6 for the real gate.
"""
    (TABLE_DIR / "synthetic_prototype_report.md").write_text(report, encoding="utf-8")

    best = metrics[
        (metrics["model"] == "random_forest")
        & (metrics["split"] == "test")
        & (metrics["horizon_hours"] == 24)
    ].iloc[0]
    model_card = f"""# Synthetic prototype model card

> **SIMULATION ONLY — NOT EVIDENCE.** This model card describes a model trained
> on generated data. It is not a model card for a real Laguna de Bay risk model.
> The real model has not been trained and the real risk assessment remains
> unavailable.

## Model details

| Field | Value |
|---|---|
| Name | HIMPIL synthetic prototype — random forest |
| Version | `synthetic-{generated_at[:10]}` |
| Type | Random forest classifier, three horizon-specific fits |
| Target | Simulated fish-kill event start within 24, 48, or 72 hours |
| Training data | Synthetic station-day panel, seed `{seed}` |
| Data origin | `synthetic_simulation` — no real observations |
| Features | {len(FEATURES)} weather, water-quality, lag, and rolling features |
| Split | Chronological: train 2021–2022, validation 2023, test 2024 |
| Artifact | `models/synthetic/random_forest_24h.joblib` and horizon variants |
| Primary test F1 (24h) | {best['f1']:.3f} (simulation only) |
| Primary test PR-AUC (24h) | {best['pr_auc']:.3f} (simulation only) |

## Intended use

- Demonstrate the modelling pipeline and rare-event evaluation code.
- Give the team a concrete artifact for code review, UI discussion, and onboarding.
- Test file layout, quarantine rules, and documentation.

## Prohibited uses

- Any real fish-kill prediction or public warning.
- Any claim about Laguna de Bay water quality, ecology, or risk.
- Any comparison with a real model, real station, real zone, or real event.
- Any defense, abstract, paper, or policy recommendation presented as evidence.
- Any use as a substitute for the Section 6 gate.

## Training data and labels

The generator creates a daily panel for six synthetic stations over four
synthetic calendar years. It injects eight simulated event periods and three
stress-only periods. Labels are derived from the simulation schedule. The model
sees only backward-looking features. Event and recovery windows are excluded from
fitting and evaluation.

## Evaluation

The test partition is the 2024 synthetic calendar. It contains two simulated
event periods. Metrics include precision, recall, F1, PR-AUC, ROC-AUC, Brier
score, and confusion-matrix counts. Positive counts are small; results are
unstable and are not estimates of real-world performance.

See [`synthetic_prototype_report.md`](synthetic_prototype_report.md) and
[`synthetic_prototype_metrics.csv`](synthetic_prototype_metrics.csv).

## Limitations

- The generator encodes a known pre-event signal; a model can learn it because
  the signal is in the simulation.
- The event schedule, station behavior, and stress periods are invented.
- No real missingness, sampling bias, measurement error, reporting delay, or
  sensor failure process is represented.
- No real spatial structure or zone crosswalk is represented.
- No real incident-reporting completeness process is represented.
- The test set is small and covers only two simulated event periods.
- Feature importance is not a causal finding.

## Ethical and operational notes

The artifact must remain in `models/synthetic/`. It must not be loaded by the real
dashboard, the real guard scripts, or any advisory service. Any screenshot or
slide that uses it must carry the “SIMULATION ONLY — NOT EVIDENCE” label.

## Maintenance

Regenerate with the fixed seed when the code changes. If the model is retained
for a demo, record the code version and seed. If real data arrive, do not
fine-tune this artifact; build a new real-data model under the Section 6 gate.
"""
    (TABLE_DIR / "synthetic_model_card.md").write_text(model_card, encoding="utf-8")


def write_manifest(
    panel: pd.DataFrame,
    events: pd.DataFrame,
    metrics: pd.DataFrame,
    seed: int,
    generated_at: str,
) -> None:
    manifest = {
        "status": "synthetic_prototype_only",
        "warning": "SIMULATION ONLY - NOT EVIDENCE",
        "data_origin": "synthetic_simulation",
        "seed": seed,
        "generated_at_utc": generated_at,
        "simulation_calendar": {"start": SIMULATION_START, "end": SIMULATION_END},
        "row_count": int(len(panel)),
        "station_count": int(panel["station_id"].nunique()),
        "event_period_count": int(
            events["period_type"].eq("synthetic_event").sum()
        ),
        "stress_period_count": int(
            events["period_type"].eq("synthetic_stress_without_event").sum()
        ),
        "split_counts": {
            str(key): int(value)
            for key, value in panel["split"].value_counts().sort_index().items()
        },
        "test_positive_counts": {
            f"y_{horizon}h": int(
                panel.loc[panel["split"] == "test", f"y_{horizon}h"].sum()
            )
            for horizon in HORIZONS
        },
        "metric_rows": int(len(metrics)),
        "quarantine": {
            "not_in_processed_data": True,
            "not_real_model_artifact": True,
            "not_connected_to_dashboard": True,
            "does_not_satisfy_model_gate": True,
        },
        "artifacts": {
            "report": "reports/tables/synthetic_prototype_report.md",
            "model_card": "reports/tables/synthetic_model_card.md",
            "metrics": "reports/tables/synthetic_prototype_metrics.csv",
            "models": "models/synthetic/",
        },
    }
    (SYNTHETIC_DATA_DIR / "synthetic_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    args = parser.parse_args()

    ensure_output_dirs()
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    panel, events = build_synthetic_dataset(args.seed)

    panel.to_csv(
        SYNTHETIC_DATA_DIR / "synthetic_station_day.csv",
        index=False,
        encoding="utf-8-sig",
    )
    events.to_csv(
        SYNTHETIC_DATA_DIR / "synthetic_event_periods.csv",
        index=False,
        encoding="utf-8-sig",
    )
    modeling_columns = [
        "date",
        "station_id",
        "zone_id",
        "split",
        "simulation_period_type",
        "synthetic_event_id",
        "synthetic_stress_id",
        "during_event",
        "recovery_window",
        "eligible_for_model",
        "target_event_id_24h",
        *FEATURES,
        *[f"y_{horizon}h" for horizon in HORIZONS],
        "data_origin",
    ]
    modeling = panel[modeling_columns].copy()
    modeling.to_csv(
        SYNTHETIC_DATA_DIR / "synthetic_modeling_dataset.csv",
        index=False,
        encoding="utf-8-sig",
    )

    model_frame = panel[
        (panel["eligible_for_model"] == 1)
        & panel[FEATURES].notna().all(axis=1)
    ].copy()
    metrics_rows, _, test_predictions, importance = fit_models(model_frame, args.seed)
    metrics = pd.DataFrame(metrics_rows)
    metrics = metrics[
        [
            "model",
            "horizon_hours",
            "split",
            "n_rows",
            "n_positive",
            "n_negative",
            "accuracy",
            "precision",
            "recall",
            "f1",
            "roc_auc",
            "pr_auc",
            "brier",
            "tn",
            "fp",
            "fn",
            "tp",
            "threshold",
        ]
    ].sort_values(["split", "horizon_hours", "model"])
    metrics.to_csv(
        TABLE_DIR / "synthetic_prototype_metrics.csv",
        index=False,
        encoding="utf-8-sig",
    )
    importance.to_csv(
        TABLE_DIR / "synthetic_feature_importance.csv",
        index=False,
        encoding="utf-8-sig",
    )
    test_predictions.to_csv(
        SYNTHETIC_DATA_DIR / "synthetic_test_predictions.csv",
        index=False,
        encoding="utf-8-sig",
    )
    detection = event_detection(test_predictions)
    detection.to_csv(
        TABLE_DIR / "synthetic_event_detection.csv",
        index=False,
        encoding="utf-8-sig",
    )

    write_report(
        panel,
        events,
        metrics,
        importance,
        detection,
        args.seed,
        generated_at,
    )
    write_manifest(panel, events, metrics, args.seed, generated_at)

    test_24 = metrics[
        (metrics["model"] == "random_forest")
        & (metrics["split"] == "test")
        & (metrics["horizon_hours"] == 24)
    ].iloc[0]
    print("Synthetic prototype complete (SIMULATION ONLY - NOT EVIDENCE).")
    print(f"Rows: {len(panel):,}; synthetic events: {len(EVENT_PERIODS)}")
    print(
        "24h test: "
        f"precision={test_24['precision']:.3f}, "
        f"recall={test_24['recall']:.3f}, "
        f"F1={test_24['f1']:.3f}, "
        f"PR-AUC={test_24['pr_auc']:.3f}"
    )
    print("Report: reports/tables/synthetic_prototype_report.md")
    print("Model card: reports/tables/synthetic_model_card.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
