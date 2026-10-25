#!/usr/bin/env python
r"""Evaluate a lead-time policy for the synthetic 24-hour model.

SIMULATION ONLY - NOT EVIDENCE

This script does not train a new model and does not modify the synthetic base
dataset or the evidence dashboard. It reads the saved synthetic event-overlay
model, reconstructs validation/test probabilities, and compares a small,
pre-specified set of alert policies:

* a day is a candidate when at least N distinct stations have a 24-hour
  probability at or above 0.5;
* a candidate becomes an issued episode only after the cooldown has elapsed;
* an event is detected when an issued episode falls within 72 hours before the
  synthetic event start and at least one affected station alerted that day.

The policy comparison is post hoc: the policies were chosen after the existing
24-hour error profile showed early alerts. It is a design exercise, not a
validated warning rule and not evidence about Laguna de Bay.

Run from the project root:

    .\.venv\Scripts\python.exe sandbox\synthetic\lead_time_policy.py
"""

from __future__ import annotations

import json
import statistics
from pathlib import Path

import joblib
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data" / "synthetic" / "base_model"
MODEL_DIR = ROOT / "models" / "synthetic" / "base_model"
REPORT_DIR = ROOT / "reports" / "tables"

PANEL_PATH = DATA_DIR / "synthetic_modeling_dataset.csv"
EVENTS_PATH = DATA_DIR / "synthetic_events.csv"
MANIFEST_PATH = DATA_DIR / "manifest.json"
TEST_PREDICTIONS_PATH = DATA_DIR / "synthetic_test_predictions.csv"
MODEL_PATH = MODEL_DIR / "random_forest_24h.joblib"

POLICY_CSV = REPORT_DIR / "synthetic_lead_time_policy.csv"
EVENT_CSV = REPORT_DIR / "synthetic_lead_time_events.csv"
REPORT_PATH = REPORT_DIR / "synthetic_lead_time_policy_report.md"

WARNING = "SIMULATION ONLY - NOT EVIDENCE"
DATA_ORIGIN = "synthetic_base_v1_event_overlay"
THRESHOLD = 0.5
LEAD_WINDOW_HOURS = 72
SPLITS = {
    "validation": ("2023-01-01", "2023-12-31"),
    "test": ("2024-01-01", "2025-12-31"),
}
POLICIES = [
    {
        "policy_id": "single_station_72h",
        "label": "1 station, 72h cooldown",
        "stations_required": 1,
        "cooldown_hours": 72,
    },
    {
        "policy_id": "two_station_no_cooldown",
        "label": "2 stations, no cooldown",
        "stations_required": 2,
        "cooldown_hours": 0,
    },
    {
        "policy_id": "two_station_72h",
        "label": "2 stations, 72h cooldown",
        "stations_required": 2,
        "cooldown_hours": 72,
    },
    {
        "policy_id": "three_station_72h",
        "label": "3 stations, 72h cooldown",
        "stations_required": 3,
        "cooldown_hours": 72,
    },
]


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame, list[str], object]:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    features = list(manifest["features"])
    panel = pd.read_csv(
        PANEL_PATH,
        parse_dates=["date"],
        low_memory=False,
    )
    events = pd.read_csv(
        EVENTS_PATH,
        parse_dates=["event_start_date", "event_end_date"],
    )
    model = joblib.load(MODEL_PATH)
    return panel, events, features, model


def probabilities_for_split(
    panel: pd.DataFrame,
    features: list[str],
    model: object,
    split_name: str,
) -> pd.DataFrame:
    frame = panel.loc[
        panel["split"].eq(split_name) & panel["model_eligible"].eq(1)
    ].copy()
    frame["probability_24h"] = model.predict_proba(frame[features])[:, 1]
    frame["alert_24h"] = (frame["probability_24h"] >= THRESHOLD).astype(int)
    return frame


def check_saved_test_probabilities(frame: pd.DataFrame) -> float:
    saved = pd.read_csv(TEST_PREDICTIONS_PATH, parse_dates=["date"])
    merged = frame[["date", "station_id", "probability_24h"]].merge(
        saved[["date", "station_id", "probability_24h"]],
        on=["date", "station_id"],
        suffixes=("_recomputed", "_saved"),
        how="inner",
    )
    if merged.empty:
        return float("nan")
    return float(
        (merged["probability_24h_recomputed"] - merged["probability_24h_saved"])
        .abs()
        .max()
    )


def candidate_days(frame: pd.DataFrame, stations_required: int) -> list[pd.Timestamp]:
    daily = (
        frame.groupby("date", as_index=False)
        .agg(alert_stations=("alert_24h", "sum"))
        .sort_values("date")
    )
    return daily.loc[
        daily["alert_stations"].ge(stations_required), "date"
    ].tolist()


def apply_cooldown(
    days: list[pd.Timestamp],
    cooldown_hours: int,
) -> list[pd.Timestamp]:
    episodes: list[pd.Timestamp] = []
    for day in sorted(days):
        if not episodes:
            episodes.append(day)
            continue
        elapsed = (day - episodes[-1]).total_seconds() / 3600
        if elapsed >= cooldown_hours:
            episodes.append(day)
    return episodes


def affected_stations(event: object) -> set[str]:
    raw = getattr(event, "affected_stations", "")
    if pd.isna(raw):
        return set()
    return {value.strip() for value in str(raw).split(";") if value.strip()}


def event_rows_for_policy(
    frame: pd.DataFrame,
    events: pd.DataFrame,
    split_name: str,
    policy: dict[str, object],
    episodes: list[pd.Timestamp],
) -> list[dict[str, object]]:
    start_date, end_date = SPLITS[split_name]
    split_events = events.loc[
        events["period_type"].eq("synthetic_event")
        & events["event_start_date"].between(start_date, end_date)
    ].sort_values("event_start_date")
    rows: list[dict[str, object]] = []

    for event in split_events.itertuples(index=False):
        window_start = event.event_start_date - pd.Timedelta(hours=LEAD_WINDOW_HOURS)
        candidate_episodes = [
            day for day in episodes if window_start <= day < event.event_start_date
        ]
        affected = affected_stations(event)
        affected_episodes = []
        for day in candidate_episodes:
            alerts = frame.loc[
                frame["date"].eq(day) & frame["alert_24h"].eq(1), "station_id"
            ]
            if affected.intersection(set(alerts)):
                affected_episodes.append(day)
        first_episode = min(affected_episodes) if affected_episodes else None
        rows.append(
            {
                "policy_id": policy["policy_id"],
                "split": split_name,
                "event_id": event.event_id,
                "event_start_date": event.event_start_date.date().isoformat(),
                "first_episode_date": (
                    first_episode.date().isoformat() if first_episode is not None else ""
                ),
                "lead_days": (
                    (event.event_start_date - first_episode).days
                    if first_episode is not None
                    else ""
                ),
                "detected": int(first_episode is not None),
                "affected_stations": event.affected_stations,
                "data_origin": DATA_ORIGIN,
                "warning": WARNING,
            }
        )
    return rows


def policy_result(
    frame: pd.DataFrame,
    policy: dict[str, object],
    split_name: str,
    event_rows: list[dict[str, object]],
) -> dict[str, object]:
    episodes = apply_cooldown(
        candidate_days(frame, int(policy["stations_required"])),
        int(policy["cooldown_hours"]),
    )
    split_events = event_rows
    detected = sum(int(row["detected"]) for row in split_events)
    leads = [
        int(row["lead_days"])
        for row in split_events
        if row["detected"] == 1 and row["lead_days"] != ""
    ]
    start_date, end_date = SPLITS[split_name]
    event_windows = [
        (
            pd.Timestamp(str(row["event_start_date"]))
            - pd.Timedelta(hours=LEAD_WINDOW_HOURS),
            pd.Timestamp(str(row["event_start_date"])),
        )
        for row in split_events
    ]
    false_episodes = 0
    for day in episodes:
        inside_event_window = any(start <= day < end for start, end in event_windows)
        if not inside_event_window:
            false_episodes += 1

    return {
        "policy_id": policy["policy_id"],
        "policy": policy["label"],
        "split": split_name,
        "stations_required": int(policy["stations_required"]),
        "cooldown_hours": int(policy["cooldown_hours"]),
        "lead_window_hours": LEAD_WINDOW_HOURS,
        "threshold": THRESHOLD,
        "raw_alert_rows": int(frame["alert_24h"].sum()),
        "episodes": len(episodes),
        "events": len(split_events),
        "events_detected": detected,
        "false_episodes": false_episodes,
        "median_lead_days": round(statistics.median(leads), 2) if leads else "",
        "mean_lead_days": round(statistics.mean(leads), 2) if leads else "",
        "min_lead_days": min(leads) if leads else "",
        "max_lead_days": max(leads) if leads else "",
        "data_origin": DATA_ORIGIN,
        "warning": WARNING,
    }


def counts_for_split(frame: pd.DataFrame) -> dict[str, int]:
    return {
        "rows": int(len(frame)),
        "raw_alerts": int(frame["alert_24h"].sum()),
        "pre_event_alerts": int(
            frame.loc[
                frame["synthetic_period_type"].eq("pre_event"), "alert_24h"
            ].sum()
        ),
        "stress_only_alerts": int(
            frame.loc[
                frame["synthetic_period_type"].eq("stress_only"), "alert_24h"
            ].sum()
        ),
        "baseline_alerts": int(
            frame.loc[
                frame["synthetic_period_type"].eq("baseline"), "alert_24h"
            ].sum()
        ),
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
    results: list[dict[str, object]],
    event_rows: list[dict[str, object]],
    split_counts: dict[str, dict[str, int]],
    test_probability_difference: float,
) -> str:
    policy_rows = [
        {
            "Split": result["split"],
            "Policy": result["policy"],
            "Episodes": result["episodes"],
            "Events detected": f"{result['events_detected']}/{result['events']}",
            "False episodes": result["false_episodes"],
            "Raw alert rows": result["raw_alert_rows"],
            "Median lead (days)": result["median_lead_days"],
        }
        for result in results
    ]
    counts_rows = [
        {
            "Split": split,
            "Rows": values["rows"],
            "Raw 24h alerts": values["raw_alerts"],
            "Pre-event alerts": values["pre_event_alerts"],
            "Stress-only alerts": values["stress_only_alerts"],
            "Baseline alerts": values["baseline_alerts"],
        }
        for split, values in split_counts.items()
    ]
    recommended = [
        row
        for row in event_rows
        if row["policy_id"] == "two_station_72h"
    ]
    recommended_rows = [
        {
            "Split": row["split"],
            "Event": row["event_id"],
            "Start": row["event_start_date"],
            "First affected episode": row["first_episode_date"] or "none",
            "Lead (days)": row["lead_days"] if row["lead_days"] != "" else "none",
            "Detected": row["detected"],
        }
        for row in recommended
    ]
    test_two = next(
        result
        for result in results
        if result["split"] == "test" and result["policy_id"] == "two_station_72h"
    )
    test_one = next(
        result
        for result in results
        if result["split"] == "test" and result["policy_id"] == "single_station_72h"
    )
    test_three = next(
        result
        for result in results
        if result["split"] == "test" and result["policy_id"] == "three_station_72h"
    )
    test_no_cooldown = next(
        result
        for result in results
        if result["split"] == "test" and result["policy_id"] == "two_station_no_cooldown"
    )
    validation_two = next(
        result
        for result in results
        if result["split"] == "validation" and result["policy_id"] == "two_station_72h"
    )

    return f"""# Synthetic lead-time policy experiment

> **{WARNING}**
>
> This is a post hoc policy exercise on the synthetic event-overlay model. It is
> not a study of Laguna de Bay, not a real warning system, and not evidence that
> fish kills can be predicted or prevented. The event dates, effects, labels, and
> probabilities are synthetic.

**Generated by:** `sandbox/synthetic/lead_time_policy.py`  
**Input model:** `models/synthetic/base_model/random_forest_24h.joblib`  
**Input panel:** `data/synthetic/base_model/synthetic_modeling_dataset.csv`  
**Synthetic schedule:** `data/synthetic/base_model/synthetic_events.csv`  
**Threshold:** `{THRESHOLD}` (the saved 24-hour model threshold, not tuned)  
**Lead window:** `{LEAD_WINDOW_HOURS}` hours before a synthetic event start  
**Seed:** `20261023` (inherited from the base model)  
**Warning:** every row carries `data_origin = {DATA_ORIGIN}` and `{WARNING}`.

## 1. Question

The saved 24-hour model flags 44 station-days in the synthetic test period:
20 are within the 24-hour target, 23 are pre-event rows 2-3 days before an
event, and 1 is a stress-only false alarm. The 23 early rows are errors under a
strict 24-hour label, but they may be useful if the intended product is a
2-3 day warning.

Can a simple confirmation and cooldown policy turn those early alerts into a
usable lead-time warning without adding false event alarms?

## 2. Policy definitions

- **Alert row:** `probability_24h >= {THRESHOLD}` for one station on one date.
- **Candidate day:** at least **N distinct stations** alert on the same date.
- **Issued episode:** a candidate day that is at least the cooldown interval
  after the previous issued episode.
- **Event detected:** an issued episode occurs within **{LEAD_WINDOW_HOURS}
  hours before** the synthetic event start and at least one affected station
  alerted that day.
- **False episode:** an issued episode that is not within any event's
  {LEAD_WINDOW_HOURS}-hour lead window. Stress-only and baseline periods are the
  only possible sources of these alarms in this test design.

Four policies are compared. They are deliberately small and interpretable, not
an exhaustive search:

1. 1 station, 72-hour cooldown.
2. 2 stations, no cooldown.
3. 2 stations, 72-hour cooldown.
4. 3 stations, 72-hour cooldown.

## 3. Raw alert counts

{markdown_table(counts_rows, ["Split", "Rows", "Raw 24h alerts", "Pre-event alerts", "Stress-only alerts", "Baseline alerts"])}

The raw alert rows do not disappear when the policy changes. A confirmation
rule reduces the number of **issued episodes**; it does not make the underlying
station-day alerts correct under the original 24-hour label.

## 4. Policy comparison

{markdown_table(policy_rows, ["Split", "Policy", "Episodes", "Events detected", "False episodes", "Raw alert rows", "Median lead (days)"])}

### Recommended-policy event detail

The 2-station, 72-hour cooldown policy is shown here because it keeps every
synthetic test event while removing the single stress-only episode. This
selection is **post hoc** and is not a validation result.

{markdown_table(recommended_rows, ["Split", "Event", "Start", "First affected episode", "Lead (days)", "Detected"])}

## 5. Reading the result

- **Test split:** the 2-station, 72-hour policy issues **{test_two['episodes']}
  episodes** for **{test_two['events']}** events, detects
  **{test_two['events_detected']}/{test_two['events']}**, and has
  **{test_two['false_episodes']} false episodes**. The first alerts arrive
  **{test_two['min_lead_days']}-{test_two['max_lead_days']} days** before the
  synthetic event starts.
- **Validation split:** the same policy issues **{validation_two['episodes']}
  episodes**, detects **{validation_two['events_detected']}/{validation_two['events']}**,
  and has **{validation_two['false_episodes']} false episodes**. The result is
  consistent in direction, but there are only two validation events.
- **Earlier warning, more noise:** 1 station with a 72-hour cooldown detects
  **{test_one['events_detected']}/{test_one['events']}** test events at a median
  lead of **3 days**, but issues **{test_one['episodes']} episodes** and
  **{test_one['false_episodes']} false episode** (the stress-only period).
- **More conservative:** 3 stations with a 72-hour cooldown also detects
  **{test_three['events_detected']}/{test_three['events']}** with
  **{test_three['false_episodes']} false episodes**, but the median lead falls
  to **{test_three['median_lead_days']} days**. It does not improve the
  false-episode count in this sample.
- **No cooldown:** 2 stations without cooldown detects all events but issues
  **{test_no_cooldown['episodes']} episodes** in the test split, more than the
  **{test_two['episodes']}** issued by the 72-hour cooldown. The cooldown is
  therefore useful for reducing repeated alerts, not for finding new events.

The 23 pre-event rows that the 24-hour label calls false positives are better
read as **early signals**. The experiment does not show that they are correct
warnings; it shows that the label horizon and the intended lead time must match.
A future real system should define the advisory lead time first, then train and
evaluate against that horizon.

## 6. Limits

- The policies were chosen after the existing 24-hour error profile was
  inspected. This is a **post hoc** exercise, not a pre-registered policy test.
- The validation split is not an independent confirmation of the selected
  policy; the policy was chosen after the test error profile was inspected.
- The confirmation rule is a decision layer on the saved model, not a newly
  trained 72-hour objective.
- The test split contains only **4** synthetic events; validation contains
  **2**. No confidence interval, significance test, or real-world generalization
  is justified.
- The event effect is injected into the same variables used as features. The
  probabilities are optimistic by construction.
- The 24-hour model is being reused as an early-signal generator. A real
  deployment should train a model against the intended lead-time label.
- Confirmation reduces issued episodes, not the raw station-day alert burden.
- The experiment does not use real daily observations, verified events,
  coordinates, or a station-to-zone crosswalk.
- No threshold tuning, probability calibration, or operational cost analysis was
  performed.
- The experiment is quarantined from `data/processed/`, `models/model.joblib`,
  and `dashboard/src/data/dashboard.json`.
- Recomputed test probabilities match the saved test predictions to within
  `{test_probability_difference:.2e}` maximum absolute difference.

## 7. Reproduce

From the project root:

```powershell
.\\.venv\\Scripts\\python.exe sandbox\\synthetic\\lead_time_policy.py
```

Outputs:

| File | Purpose |
|---|---|
| `reports/tables/synthetic_lead_time_policy.csv` | Policy comparison by split |
| `reports/tables/synthetic_lead_time_events.csv` | Event-level first detection and lead time |
| `reports/tables/synthetic_lead_time_policy_report.md` | This report |

The script is read-only with respect to the base dataset, the base model, and the
evidence dashboard. It writes only the three report artifacts above.

> **{WARNING}**
"""


def main() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    panel, events, features, model = load_inputs()

    frames = {
        split_name: probabilities_for_split(panel, features, model, split_name)
        for split_name in SPLITS
    }
    test_probability_difference = check_saved_test_probabilities(frames["test"])
    split_counts = {
        split_name: counts_for_split(frame) for split_name, frame in frames.items()
    }

    all_results: list[dict[str, object]] = []
    all_event_rows: list[dict[str, object]] = []
    for split_name, frame in frames.items():
        for policy in POLICIES:
            event_rows = event_rows_for_policy(
                frame, events, split_name, policy, apply_cooldown(
                    candidate_days(frame, int(policy["stations_required"])),
                    int(policy["cooldown_hours"]),
                )
            )
            all_event_rows.extend(event_rows)
            all_results.append(policy_result(frame, policy, split_name, event_rows))

    policy_frame = pd.DataFrame(all_results)
    event_frame = pd.DataFrame(all_event_rows)
    policy_frame.to_csv(POLICY_CSV, index=False)
    event_frame.to_csv(EVENT_CSV, index=False)
    REPORT_PATH.write_text(
        build_report(
            all_results,
            all_event_rows,
            split_counts,
            test_probability_difference,
        ),
        encoding="utf-8",
    )

    print(WARNING)
    print(f"Wrote {POLICY_CSV.relative_to(ROOT)}")
    print(f"Wrote {EVENT_CSV.relative_to(ROOT)}")
    print(f"Wrote {REPORT_PATH.relative_to(ROOT)}")
    print(f"Saved-test probability max difference: {test_probability_difference:.2e}")
    for split_name in SPLITS:
        for policy in POLICIES:
            row = policy_frame.loc[
                policy_frame["split"].eq(split_name)
                & policy_frame["policy_id"].eq(policy["policy_id"])
            ].iloc[0]
            print(
                f"  {split_name:10s} {row['policy']:32s} "
                f"episodes={row['episodes']:>2} "
                f"detected={row['events_detected']}/{row['events']} "
                f"false={row['false_episodes']} "
                f"median_lead={row['median_lead_days']}"
            )


if __name__ == "__main__":
    main()
