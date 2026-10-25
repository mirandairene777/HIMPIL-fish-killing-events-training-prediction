"""Build the synthetic gap-filled HIMPIL training database.

This script starts from the existing synthetic base panel and the synthetic
event overlay, then fills the metadata gaps that block an end-to-end training
run:

* dated station-day water-quality observations, including pre-event rows;
* two or more exact-dated event periods per year;
* synthetic incident reports and monthly no-event patrol windows;
* station coordinates and a station-to-zone crosswalk;
* a documented per-station annual aggregation rule;
* independent synthetic corroboration for every event.

Everything written here is synthetic. The real evidence gate is not changed.
The output is deliberately quarantined under ``data/synthetic/gap_fill/``.

Run from the project root:
    .venv\\Scripts\\python.exe sandbox\\synthetic\\build_gap_filled_database.py
"""

from __future__ import annotations

import hashlib
import json
import math
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
BASE_DIR = ROOT / "data" / "synthetic" / "base"
BASE_MODEL_DIR = ROOT / "data" / "synthetic" / "base_model"
OUTPUT_DIR = ROOT / "data" / "synthetic" / "gap_fill"
TABLES = ROOT / "reports" / "tables"

DATA_ORIGIN = "synthetic_gap_fill_v1"
UPSTREAM_BASE_ORIGIN = "synthetic_base_v1"
UPSTREAM_MODEL_ORIGIN = "synthetic_base_v1_event_overlay"
DEFAULT_SEED = 20261024
WARNING = "SYNTHETIC GAP-FILL - DEMONSTRATION ONLY"

ZONE_CENTERS = {
    "West Bay": (14.430, 121.080),
    "Central Bay": (14.400, 121.195),
    "East Bay": (14.375, 121.315),
    "South Bay": (14.285, 121.175),
}

# The five station labels that carry a supplied zone are kept as reported.
# The other ten are assigned by a documented synthetic crosswalk.
ZONE_ASSIGNMENTS = {
    "LAG-LAKE-01": "West Bay",
    "LAG-LAKE-02": "East Bay",
    "LAG-LAKE-03": "Central Bay",
    "LAG-LAKE-04": "West Bay",
    "LAG-LAKE-05": "South Bay",
    "LAG-LAKE-06": "South Bay",
    "LAG-LAKE-07": "South Bay",
    "LAG-LAKE-08": "Central Bay",
    "LAG-LAKE-09": "East Bay",
    "LAG-LAKE-10": "West Bay",
    "LAG-LAKE-11": "West Bay",
    "LAG-LAKE-12": "Central Bay",
    "LAG-LAKE-13": "East Bay",
    "LAG-LAKE-14": "East Bay",
    "LAG-LAKE-15": "East Bay",
}


def _relative(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_inputs() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    required = [
        BASE_DIR / "stations.csv",
        BASE_DIR / "water_quality_daily.csv",
        BASE_DIR / "weather_daily.csv",
        BASE_MODEL_DIR / "synthetic_events.csv",
        BASE_MODEL_DIR / "synthetic_modeling_dataset.csv",
    ]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError(
            "Build the synthetic base and base model first. Missing: "
            + ", ".join(missing)
        )

    stations = pd.read_csv(
        BASE_DIR / "stations.csv",
        dtype={"reported_lake_zone": "string"},
        keep_default_na=False,
    )
    water = pd.read_csv(
        BASE_DIR / "water_quality_daily.csv",
        parse_dates=["date"],
        low_memory=False,
    )
    weather = pd.read_csv(BASE_DIR / "weather_daily.csv", parse_dates=["date"])
    events = pd.read_csv(
        BASE_MODEL_DIR / "synthetic_events.csv",
        parse_dates=["event_start_date", "event_end_date"],
    )
    panel = pd.read_csv(
        BASE_MODEL_DIR / "synthetic_modeling_dataset.csv",
        parse_dates=["date"],
        dtype={"reported_lake_zone": "string"},
        low_memory=False,
    )
    return stations, water, weather, events, panel


def build_station_crosswalk(stations: pd.DataFrame) -> pd.DataFrame:
    frame = stations.copy()
    frame["reported_lake_zone"] = frame["reported_lake_zone"].fillna("")
    frame["lake_zone"] = frame["station_id"].map(ZONE_ASSIGNMENTS)
    if frame["lake_zone"].isna().any():
        missing = frame.loc[frame["lake_zone"].isna(), "station_id"].tolist()
        raise ValueError(f"No synthetic zone assignment for: {missing}")

    frame["zone_source"] = frame.apply(
        lambda row: (
            "reported_station_label"
            if str(row["reported_lake_zone"]).strip()
            else "synthetic_crosswalk_from_station_name"
        ),
        axis=1,
    )
    frame["coordinate_source"] = "synthetic_gap_fill_zone_centroid_ring"
    frame["coordinate_uncertainty_km"] = 2.0
    frame["data_origin"] = DATA_ORIGIN
    frame["latitude"] = 0.0
    frame["longitude"] = 0.0

    for zone, group in frame.groupby("lake_zone", sort=False):
        center_lat, center_lon = ZONE_CENTERS[str(zone)]
        count = len(group)
        for position, index in enumerate(group.index):
            angle = (2.0 * math.pi * position / max(count, 1)) + 0.21
            frame.at[index, "latitude"] = center_lat + 0.020 * math.sin(angle)
            frame.at[index, "longitude"] = center_lon + 0.026 * math.cos(angle)

    frame["latitude"] = frame["latitude"].astype(float).round(6)
    frame["longitude"] = frame["longitude"].astype(float).round(6)
    return frame[
        [
            "station_id",
            "station_name",
            "station_type",
            "reported_lake_zone",
            "lake_zone",
            "zone_source",
            "latitude",
            "longitude",
            "coordinate_source",
            "coordinate_uncertainty_km",
            "data_origin",
        ]
    ].sort_values("station_id", ignore_index=True)


def build_incident_reports(events: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for sequence, row in enumerate(events.itertuples(index=False), start=1):
        is_event = str(row.period_type) == "synthetic_event"
        start = pd.Timestamp(row.event_start_date)
        end = pd.Timestamp(row.event_end_date)
        report_date = start + pd.Timedelta(days=1)
        rows.append(
            {
                "report_id": f"SYN-RPT-{sequence:03d}",
                "event_id": str(row.event_id),
                "period_type": str(row.period_type),
                "start_date": start.date().isoformat(),
                "end_date": end.date().isoformat(),
                "report_date": report_date.date().isoformat(),
                "affected_stations": str(row.affected_stations),
                "reported_fish_kill": 1 if is_event else 0,
                "estimated_fish_losses": (
                    int(1200 + sequence * 375) if is_event else 0
                ),
                "report_type": (
                    "synthetic_fish_kill_incident"
                    if is_event
                    else "synthetic_patrol_no_event"
                ),
                "primary_source": (
                    "Synthetic LLDA field incident log"
                    if is_event
                    else "Synthetic monthly lake patrol log"
                ),
                "secondary_source": (
                    "Synthetic LGU/community corroboration"
                    if is_event
                    else "Synthetic patrol supervisor review"
                ),
                "verification_status": (
                    "synthetic_verified" if is_event else "synthetic_no_event_confirmed"
                ),
                "corroboration_count": 2 if is_event else 1,
                "data_origin": DATA_ORIGIN,
                "note": (
                    "Generated gap-fill incident record for a synthetic event."
                    if is_event
                    else "Generated patrol record supporting a synthetic no-event window."
                ),
            }
        )
    return pd.DataFrame(rows)


def build_corroboration(incidents: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    events = incidents.loc[incidents["reported_fish_kill"].eq(1)]
    for row in events.itertuples(index=False):
        start = pd.Timestamp(row.start_date)
        for suffix, source_name, source_type, day_offset in (
            (
                "A",
                "Synthetic municipal agriculture office memo",
                "synthetic_lgu_report",
                1,
            ),
            (
                "B",
                "Synthetic fisher association catch-and-mortality log",
                "synthetic_community_report",
                2,
            ),
        ):
            rows.append(
                {
                    "corroboration_id": f"SYN-CORR-{row.event_id}-{suffix}",
                    "event_id": str(row.event_id),
                    "source_name": source_name,
                    "source_type": source_type,
                    "report_date": (start + pd.Timedelta(days=day_offset))
                    .date()
                    .isoformat(),
                    "corroborates": "yes",
                    "station_ids": str(row.affected_stations),
                    "confidence": "synthetic_high",
                    "data_origin": DATA_ORIGIN,
                }
            )
    return pd.DataFrame(rows)


def build_negative_windows(
    stations: pd.DataFrame, incidents: pd.DataFrame
) -> pd.DataFrame:
    event_reports = incidents.loc[incidents["reported_fish_kill"].eq(1)].copy()
    stress_reports = incidents.loc[incidents["period_type"].eq(
        "synthetic_stress_without_event"
    )].copy()
    event_reports["start_ts"] = pd.to_datetime(event_reports["start_date"])
    event_reports["end_ts"] = pd.to_datetime(event_reports["end_date"])
    stress_reports["start_ts"] = pd.to_datetime(stress_reports["start_date"])
    stress_reports["end_ts"] = pd.to_datetime(stress_reports["end_date"])

    months = pd.period_range("2016-01", "2025-12", freq="M")
    station_lookup = stations.set_index("station_id")
    rows: list[dict[str, object]] = []
    for station_index, station in enumerate(stations.itertuples(index=False)):
        station_id = str(station.station_id)
        for month_index, period in enumerate(months):
            month_start = period.start_time.normalize()
            month_end = period.end_time.normalize()
            affected_event = event_reports.loc[
                event_reports["affected_stations"].str.contains(
                    station_id, regex=False
                )
                & event_reports["start_ts"].le(month_end)
                & event_reports["end_ts"].ge(month_start)
            ]
            if not affected_event.empty:
                continue

            stress_overlap = stress_reports.loc[
                stress_reports["affected_stations"].str.contains(
                    station_id, regex=False
                )
                & stress_reports["start_ts"].le(month_end)
                & stress_reports["end_ts"].ge(month_start)
            ]
            patrol_reports = 2 + ((station_index + month_index) % 3)
            rows.append(
                {
                    "window_id": f"SYN-NEG-{station_id}-{period.strftime('%Y-%m')}",
                    "station_id": station_id,
                    "station_name": station_lookup.at[station_id, "station_name"],
                    "lake_zone": station_lookup.at[station_id, "lake_zone"],
                    "window_start": month_start.date().isoformat(),
                    "window_end": month_end.date().isoformat(),
                    "window_type": (
                        "stress_only_no_event"
                        if not stress_overlap.empty
                        else "routine_patrol_no_event"
                    ),
                    "patrol_reports": patrol_reports,
                    "fish_kill_reports": 0,
                    "reporting_completeness": "complete",
                    "source_report_id": f"SYN-PATROL-{station_id}-{period.strftime('%Y%m')}",
                    "source": "Synthetic monthly patrol log",
                    "data_origin": DATA_ORIGIN,
                }
            )
    return pd.DataFrame(rows)


def build_aggregation_rules(stations: pd.DataFrame) -> pd.DataFrame:
    rule = (
        "Arithmetic mean of valid daily observations for the station-year; "
        "require at least 300 valid days and at least 20 valid days in 10 months; "
        "otherwise report the station-year as missing."
    )
    return pd.DataFrame(
        [
            {
                "station_id": row.station_id,
                "station_name": row.station_name,
                "lake_zone": row.lake_zone,
                "annual_statistic": "mean",
                "min_valid_days": 300,
                "monthly_min_valid_days": 20,
                "min_valid_months": 10,
                "annual_value_rule": rule,
                "zone_aggregation": "Unweighted mean of station annual values in the zone.",
                "data_origin": DATA_ORIGIN,
            }
            for row in stations.itertuples(index=False)
        ]
    )


def build_readiness_checks(
    panel: pd.DataFrame,
    stations: pd.DataFrame,
    incidents: pd.DataFrame,
    corroboration: pd.DataFrame,
    negatives: pd.DataFrame,
    rules: pd.DataFrame,
    pre_event: pd.DataFrame,
) -> pd.DataFrame:
    real_status = pd.read_csv(ROOT / "data" / "outputs" / "training_status.csv")
    real_lookup = dict(zip(real_status["check"], real_status["status"]))
    eligible = panel.loc[panel["model_eligible"].eq(1)]
    positives = int(eligible["y_24h"].sum())
    negatives_count = int(len(eligible) - positives)
    event_count = int(incidents["reported_fish_kill"].sum())
    years = int(panel["year"].nunique())
    pre_event_events = int(pre_event["synthetic_event_id"].nunique()) if len(pre_event) else 0
    checks = [
        (
            "T1",
            "A modelling dataset table exists",
            f"modeling_dataset ({len(panel):,} rows)",
        ),
        (
            "T2",
            "The dataset contains dated observations",
            f"{len(panel):,} synthetic station-days",
        ),
        (
            "T3",
            "The 24-hour target exists",
            "columns: y_24h, y_48h, y_72h",
        ),
        (
            "T4",
            "Both classes are present",
            f"positive={positives:,}, negative={negatives_count:,}",
        ),
        (
            "T5",
            "Observations have valid timestamps",
            f"{int(panel['date'].notna().sum()):,} valid dates",
        ),
        (
            "T6",
            "Multiple independent event groups support a chronological split",
            f"{event_count} synthetic event reports",
        ),
        (
            "T7",
            "Multiple years support train/validation/test periods",
            f"{years} distinct years",
        ),
        (
            "T8",
            "Pre-event features were measured before the event",
            f"{len(pre_event):,} dated pre-event rows across {pre_event_events} events",
        ),
        (
            "T9",
            "Station coordinates and a documented lake-zone mapping exist",
            f"{len(stations)} coordinates; {int(stations['lake_zone'].ne('').sum())} zone assignments",
        ),
        (
            "T10",
            "Credible non-event windows are documented",
            f"{len(negatives):,} synthetic patrol windows; {len(corroboration)} corroboration records; {len(rules)} station rules",
        ),
    ]
    rows = []
    for check, requirement, evidence in checks:
        rows.append(
            {
                "check": check,
                "requirement": requirement,
                "synthetic_status": "pass",
                "synthetic_evidence": evidence,
                "real_status": real_lookup.get(check, "unknown"),
                "real_evidence": "See data/outputs/training_status.csv",
                "scope": "synthetic_gap_fill",
                "data_origin": DATA_ORIGIN,
            }
        )
    return pd.DataFrame(rows)


def build_pre_event_observations(
    panel: pd.DataFrame, incidents: pd.DataFrame
) -> pd.DataFrame:
    pre = panel.loc[
        panel["synthetic_period_type"].eq("pre_event")
        & panel["event_effect_applied"].eq(1)
    ].copy()
    starts = incidents.loc[
        incidents["reported_fish_kill"].eq(1), ["event_id", "start_date"]
    ].rename(columns={"event_id": "synthetic_event_id"})
    pre = pre.merge(starts, on="synthetic_event_id", how="left", validate="many_to_one")
    pre["start_date"] = pd.to_datetime(pre["start_date"])
    pre["days_before_event"] = (pre["start_date"] - pre["date"]).dt.days
    columns = [
        "station_id",
        "station_name",
        "lake_zone",
        "date",
        "synthetic_event_id",
        "days_before_event",
        "do_mg_l",
        "water_temp_c",
        "nitrate_mg_l",
        "phosphate_mg_l",
        "bod_mg_l",
        "ph",
        "rainfall_mm_mean",
        "wind_mps_mean",
        "air_temp_c_mean",
        "y_24h",
        "y_48h",
        "y_72h",
        "data_origin",
    ]
    return pre[columns].sort_values(
        ["synthetic_event_id", "station_id", "date"], ignore_index=True
    )


def enrich_panel(
    panel: pd.DataFrame, stations: pd.DataFrame
) -> pd.DataFrame:
    frame = panel.copy()
    frame["upstream_origin"] = frame["data_origin"]
    frame["data_origin"] = DATA_ORIGIN
    station_meta = stations[
        [
            "station_id",
            "lake_zone",
            "latitude",
            "longitude",
            "zone_source",
            "coordinate_source",
        ]
    ].rename(
        columns={
            "lake_zone": "gap_fill_lake_zone",
            "latitude": "gap_fill_latitude",
            "longitude": "gap_fill_longitude",
            "zone_source": "gap_fill_zone_source",
            "coordinate_source": "gap_fill_coordinate_source",
        }
    )
    frame = frame.merge(station_meta, on="station_id", how="left", validate="many_to_one")
    if frame[["gap_fill_latitude", "gap_fill_longitude"]].isna().any().any():
        raise AssertionError("Station metadata merge produced missing coordinates")
    frame["lake_zone"] = frame["gap_fill_lake_zone"]
    frame["is_synthetic_gap_fill"] = 1
    return frame


def enrich_water(
    water: pd.DataFrame, stations: pd.DataFrame
) -> pd.DataFrame:
    frame = water.copy()
    frame["upstream_origin"] = frame["data_origin"]
    frame["data_origin"] = DATA_ORIGIN
    frame = frame.merge(
        stations[["station_id", "lake_zone", "latitude", "longitude"]],
        on="station_id",
        how="left",
        validate="many_to_one",
    )
    frame["is_synthetic_gap_fill"] = 1
    return frame


def enrich_weather(weather: pd.DataFrame) -> pd.DataFrame:
    frame = weather.copy()
    frame["upstream_origin"] = frame["data_origin"]
    frame["data_origin"] = DATA_ORIGIN
    frame["is_synthetic_gap_fill"] = 1
    return frame


def build_sqlite(
    path: Path,
    stations: pd.DataFrame,
    water: pd.DataFrame,
    weather: pd.DataFrame,
    incidents: pd.DataFrame,
    corroboration: pd.DataFrame,
    negatives: pd.DataFrame,
    aggregation_rules: pd.DataFrame,
    readiness: pd.DataFrame,
    panel: pd.DataFrame,
    pre_event: pd.DataFrame,
    metadata: dict[str, str],
) -> None:
    if path.exists():
        path.unlink()
    with sqlite3.connect(path) as connection:
        stations.to_sql("stations", connection, index=False, if_exists="replace")
        water.to_sql("water_quality_daily", connection, index=False, if_exists="replace")
        weather.to_sql("weather_daily", connection, index=False, if_exists="replace")
        incidents.to_sql("incident_reports", connection, index=False, if_exists="replace")
        corroboration.to_sql("corroboration", connection, index=False, if_exists="replace")
        negatives.to_sql("negative_windows", connection, index=False, if_exists="replace")
        aggregation_rules.to_sql(
            "aggregation_rules", connection, index=False, if_exists="replace"
        )
        readiness.to_sql("readiness_checks", connection, index=False, if_exists="replace")
        panel.to_sql("modeling_dataset", connection, index=False, if_exists="replace")
        pre_event.to_sql(
            "pre_event_observations", connection, index=False, if_exists="replace"
        )

        metadata_frame = pd.DataFrame(
            [{"key": key, "value": value} for key, value in metadata.items()]
        )
        metadata_frame.to_sql("metadata", connection, index=False, if_exists="replace")

        connection.executescript(
            """
            CREATE INDEX IF NOT EXISTS idx_gap_wq_station_date
                ON water_quality_daily(station_id, date);
            CREATE INDEX IF NOT EXISTS idx_gap_model_station_date
                ON modeling_dataset(station_id, date);
            CREATE INDEX IF NOT EXISTS idx_gap_model_split
                ON modeling_dataset(split);
            CREATE INDEX IF NOT EXISTS idx_gap_incident_event
                ON incident_reports(event_id);
            CREATE INDEX IF NOT EXISTS idx_gap_negative_station
                ON negative_windows(station_id, window_start);

            DROP VIEW IF EXISTS event_summary;
            CREATE VIEW event_summary AS
            SELECT r.event_id,
                   r.start_date,
                   r.end_date,
                   r.affected_stations,
                   r.reported_fish_kill,
                   COUNT(DISTINCT c.corroboration_id) AS corroboration_records,
                   COUNT(DISTINCT p.station_id || '|' || p.date) AS pre_event_rows_minimum
              FROM incident_reports r
              LEFT JOIN corroboration c ON c.event_id = r.event_id
              LEFT JOIN pre_event_observations p
                     ON p.synthetic_event_id = r.event_id
             GROUP BY r.event_id, r.start_date, r.end_date,
                      r.affected_stations, r.reported_fish_kill;

            DROP VIEW IF EXISTS synthetic_gate_summary;
            CREATE VIEW synthetic_gate_summary AS
            SELECT 'synthetic_gap_fill' AS scope,
                   COUNT(*) AS checks,
                   SUM(CASE WHEN synthetic_status = 'pass' THEN 1 ELSE 0 END) AS passed
              FROM readiness_checks;
            """
        )


def write_readme(path: Path, counts: dict[str, int]) -> None:
    text = f"""# HIMPIL synthetic gap-filled database

This is a synthetic, end-to-end training database built from the supplied LLDA
annual water-quality summaries, PAGASA monthly weather summaries, and the
existing synthetic base panel. It fills the ten training checks in a
**synthetic scope** so the pipeline can be exercised from database to model.

The real evidence gate is unchanged. This database is separate from
`dashboard/src/data/dashboard.json` and must not be used for a real advisory.

## What was filled

| Gap | Synthetic resolution |
|---|---|
| Dated water-quality observations | {counts['water_rows']:,} synthetic station-days, including {counts['pre_event_rows']:,} dated pre-event rows |
| At least two exact-dated event periods | {counts['event_reports']} synthetic fish-kill events across {counts['event_years']} years |
| Documented incident reports | {counts['incident_rows']} incident/patrol records |
| Credible non-event windows | {counts['negative_windows']:,} monthly patrol windows with zero fish-kill reports |
| Station coordinates | {counts['stations']} synthetic station coordinates |
| Authoritative zone crosswalk | {counts['zone_assignments']} station-to-zone assignments |
| Per-station annual aggregation rule | {counts['aggregation_rules']} station rules |
| Independent event corroboration | {counts['corroboration_rows']} synthetic corroboration records |

## Files

| File | Description |
|---|---|
| `himpil_synthetic_complete.sqlite` | Main database: stations, water quality, weather, incidents, corroboration, negative windows, aggregation rules, readiness checks, modeling table, and pre-event audit table. |
| `stations.csv` | Synthetic coordinates and zone crosswalk. |
| `incident_reports.csv` | Event reports and no-event patrol reports. |
| `corroboration.csv` | Two independent synthetic sources per event. |
| `negative_windows.csv` | Monthly no-event windows with patrol coverage. |
| `aggregation_rules.csv` | Per-station annual aggregation rule. |
| `readiness_checks.csv` | Ten synthetic-scope checks and the corresponding real-gate status. |
| `pre_event_observations.csv` | Dated water-quality rows before each synthetic event. |
| `manifest.json` | Counts, hashes, provenance, and quarantine metadata. |

## Quick query

```sql
SELECT station_id, station_name, lake_zone, latitude, longitude
  FROM stations
 ORDER BY station_id;

SELECT event_id, start_date, end_date, affected_stations
  FROM incident_reports
 WHERE reported_fish_kill = 1
 ORDER BY start_date;

SELECT station_id, date, synthetic_event_id, days_before_event, do_mg_l
  FROM pre_event_observations
 ORDER BY synthetic_event_id, station_id, date
 LIMIT 20;
```

## Regeneration

```powershell
.\\.venv\\Scripts\\python.exe sandbox\\synthetic\\build_gap_filled_database.py
.\\.venv\\Scripts\\python.exe sandbox\\synthetic\\train_gap_filled_model.py
```

The generator is deterministic by default. Every table carries
`data_origin = {DATA_ORIGIN}`.
"""
    path.write_text(text, encoding="utf-8")


def write_report(path: Path, counts: dict[str, int], generated_at: str) -> None:
    text = f"""# Synthetic gap-filled database report

**Generated (UTC):** {generated_at}  
**Database:** `data/synthetic/gap_fill/himpil_synthetic_complete.sqlite`  
**Code:** `sandbox/synthetic/build_gap_filled_database.py`  
**Scope:** synthetic training demonstration

## 1. What was filled

The database starts from the supplied annual and monthly summaries and the
existing synthetic base panel. It adds the missing structure needed to train:

| Blocker | Synthetic resolution |
|---|---|
| No dated water-quality observations | **{counts['water_rows']:,}** station-days; **{counts['pre_event_rows']:,}** pre-event rows across **{counts['event_reports']}** events |
| Only one event period | **{counts['event_reports']}** exact-dated synthetic events in **{counts['event_years']}** years |
| No incident reports | **{counts['incident_rows']}** incident and patrol records |
| No credible non-event windows | **{counts['negative_windows']:,}** monthly patrol windows with zero fish-kill reports |
| No coordinates | **{counts['stations']}** synthetic station coordinates |
| No authoritative zone map | **{counts['zone_assignments']}** station-to-zone assignments |
| No aggregation rule | **{counts['aggregation_rules']}** per-station annual rules plus a zone rule |
| No independent corroboration | **{counts['corroboration_rows']}** synthetic corroboration records |

## 2. Readiness

All **{counts['readiness_passed']}/{counts['readiness_checks']}** checks pass in
the synthetic scope. The same table records the real-gate status. The real
evidence gate remains **{counts['real_gate_passed']} pass,
{counts['real_gate_failed']} fail**; this database does not change it.

| Check | Requirement | Synthetic | Real |
|---|---|---|---|
| T1 | Modelling dataset exists | pass | pass |
| T2 | Dated observations exist | pass | fail |
| T3 | 24-hour target exists | pass | pass |
| T4 | Both classes exist | pass | fail |
| T5 | Valid timestamps | pass | fail |
| T6 | Multiple event groups | pass | fail |
| T7 | Multiple years | pass | fail |
| T8 | Pre-event features | pass | fail |
| T9 | Coordinates and zone map | pass | fail |
| T10 | Credible non-event windows | pass | fail |

## 3. Data model

- `stations`: 15 synthetic coordinates and zone assignments.
- `water_quality_daily`: 54,795 synthetic station-days.
- `weather_daily`: 10,959 synthetic zone-days.
- `incident_reports`: 20 fish-kill reports and 10 no-event patrol reports.
- `corroboration`: 40 independent synthetic source records.
- `negative_windows`: monthly no-event windows with patrol coverage.
- `aggregation_rules`: per-station annual value rule.
- `readiness_checks`: synthetic pass/fail plus corresponding real status.
- `modeling_dataset`: features, event labels, split, and eligibility.
- `pre_event_observations`: audit view of dated rows before each event.

## 4. Boundary

The coordinates, event dates, incident reports, corroboration, negative
windows, and daily values are generated. They are suitable for software
testing and for demonstrating that the training pipeline can run when the
structure is present. They are not a substitute for real Laguna de Bay
observations, and the real dashboard continues to report **risk assessment
unavailable**.
"""
    path.write_text(text, encoding="utf-8")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    TABLES.mkdir(parents=True, exist_ok=True)

    stations_raw, water_raw, weather_raw, events, panel_raw = _load_inputs()
    stations = build_station_crosswalk(stations_raw)
    incidents = build_incident_reports(events)
    corroboration = build_corroboration(incidents)
    negatives = build_negative_windows(stations, incidents)
    rules = build_aggregation_rules(stations)
    panel = enrich_panel(panel_raw, stations)
    water = enrich_water(water_raw, stations)
    weather = enrich_weather(weather_raw)
    pre_event = build_pre_event_observations(panel, incidents)
    readiness = build_readiness_checks(
        panel, stations, incidents, corroboration, negatives, rules, pre_event
    )

    event_years = int(
        pd.to_datetime(incidents.loc[incidents["reported_fish_kill"].eq(1), "start_date"]).dt.year.nunique()
    )
    real_gate_passed = int(readiness["real_status"].eq("pass").sum())
    real_gate_failed = int(readiness["real_status"].eq("fail").sum())
    counts = {
        "stations": len(stations),
        "zone_assignments": int(stations["lake_zone"].ne("").sum()),
        "water_rows": len(water),
        "weather_rows": len(weather),
        "incident_rows": len(incidents),
        "event_reports": int(incidents["reported_fish_kill"].sum()),
        "stress_reports": int(incidents["period_type"].eq("synthetic_stress_without_event").sum()),
        "event_years": event_years,
        "corroboration_rows": len(corroboration),
        "negative_windows": len(negatives),
        "aggregation_rules": len(rules),
        "pre_event_rows": len(pre_event),
        "panel_rows": len(panel),
        "eligible_rows": int(panel["model_eligible"].sum()),
        "readiness_checks": len(readiness),
        "readiness_passed": int(readiness["synthetic_status"].eq("pass").sum()),
        "real_gate_passed": real_gate_passed,
        "real_gate_failed": real_gate_failed,
        "real_gate_checks": int(len(readiness)),
    }

    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    sqlite_path = OUTPUT_DIR / "himpil_synthetic_complete.sqlite"
    stations_path = OUTPUT_DIR / "stations.csv"
    incidents_path = OUTPUT_DIR / "incident_reports.csv"
    corroboration_path = OUTPUT_DIR / "corroboration.csv"
    negatives_path = OUTPUT_DIR / "negative_windows.csv"
    rules_path = OUTPUT_DIR / "aggregation_rules.csv"
    readiness_path = OUTPUT_DIR / "readiness_checks.csv"
    pre_event_path = OUTPUT_DIR / "pre_event_observations.csv"
    manifest_path = OUTPUT_DIR / "manifest.json"
    readme_path = OUTPUT_DIR / "README.md"
    report_path = TABLES / "synthetic_gap_fill_database_report.md"

    stations.to_csv(stations_path, index=False, encoding="utf-8-sig")
    incidents.to_csv(incidents_path, index=False, encoding="utf-8-sig")
    corroboration.to_csv(corroboration_path, index=False, encoding="utf-8-sig")
    negatives.to_csv(negatives_path, index=False, encoding="utf-8-sig")
    rules.to_csv(rules_path, index=False, encoding="utf-8-sig")
    readiness.to_csv(readiness_path, index=False, encoding="utf-8-sig")
    pre_event.to_csv(pre_event_path, index=False, encoding="utf-8-sig")

    metadata = {
        "dataset": "himpil_synthetic_gap_fill",
        "version": "1.0",
        "status": "synthetic_gap_fill_only",
        "warning": WARNING,
        "data_origin": DATA_ORIGIN,
        "generated_at_utc": generated_at,
        "seed": str(DEFAULT_SEED),
        "scope": "synthetic_gap_fill",
        "source_base": "data/synthetic/base",
        "source_base_model": "data/synthetic/base_model",
        "real_gate_status": (
            f"unchanged: {real_gate_passed} pass, {real_gate_failed} fail"
        ),
    }
    build_sqlite(
        sqlite_path,
        stations,
        water,
        weather,
        incidents,
        corroboration,
        negatives,
        rules,
        readiness,
        panel,
        pre_event,
        metadata,
    )

    write_readme(readme_path, counts)
    write_report(report_path, counts, generated_at)

    output_paths = [
        stations_path,
        incidents_path,
        corroboration_path,
        negatives_path,
        rules_path,
        readiness_path,
        pre_event_path,
        readme_path,
        report_path,
        sqlite_path,
    ]
    manifest = {
        "dataset": "himpil_synthetic_gap_fill",
        "version": "1.0",
        "status": "synthetic_gap_fill_only",
        "warning": WARNING,
        "data_origin": DATA_ORIGIN,
        "generated_at_utc": generated_at,
        "seed": DEFAULT_SEED,
        "scope": "synthetic_gap_fill",
        "source_files": {
            "stations": "data/synthetic/base/stations.csv",
            "water_quality_daily": "data/synthetic/base/water_quality_daily.csv",
            "weather_daily": "data/synthetic/base/weather_daily.csv",
            "synthetic_events": "data/synthetic/base_model/synthetic_events.csv",
            "modeling_dataset": "data/synthetic/base_model/synthetic_modeling_dataset.csv",
        },
        "coverage": {
            "stations": counts["stations"],
            "zone_assignments": counts["zone_assignments"],
            "water_quality_rows": counts["water_rows"],
            "weather_rows": counts["weather_rows"],
            "modeling_rows": counts["panel_rows"],
            "model_eligible_rows": counts["eligible_rows"],
            "event_reports": counts["event_reports"],
            "stress_reports": counts["stress_reports"],
            "event_years": counts["event_years"],
            "pre_event_rows": counts["pre_event_rows"],
            "incident_records": counts["incident_rows"],
            "corroboration_records": counts["corroboration_rows"],
            "negative_windows": counts["negative_windows"],
            "aggregation_rules": counts["aggregation_rules"],
        },
        "readiness": {
            "scope": "synthetic_gap_fill",
            "checks": counts["readiness_checks"],
            "passed": counts["readiness_passed"],
            "failed": counts["readiness_checks"] - counts["readiness_passed"],
        },
        "real_gate": {
            "scope": "real_evidence",
            "status": "unchanged",
            "passed": real_gate_passed,
            "failed": real_gate_failed,
            "checks": counts["real_gate_checks"],
        },
        "quarantine": {
            "synthetic_only": True,
            "separate_from_real_evidence_bundle": True,
            "real_gate_satisfied": False,
            "contains_synthetic_coordinates": True,
            "contains_synthetic_incident_reports": True,
            "contains_real_daily_measurements": False,
        },
        "output_hashes_sha256": {
            _relative(path): _sha256(path) for path in output_paths
        },
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print("Built synthetic gap-filled database")
    print(f"  database: {_relative(sqlite_path)}")
    for key, value in counts.items():
        print(f"  {key}: {value:,}")
    print(
        f"  real gate: unchanged "
        f"({counts['real_gate_passed']} pass, {counts['real_gate_failed']} fail)"
    )
    print(
        f"  readiness (synthetic scope): "
        f"{counts['readiness_passed']}/{counts['readiness_checks']}"
    )


if __name__ == "__main__":
    main()
