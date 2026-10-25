"""
HIMPIL Phases 4-5 - test whether supervised labels are scientifically supported.

No label is created when the evidence is insufficient. This script writes an
auditable readiness table, an empty schema for future data, and a documented
label definition that is marked NOT ACTIVE.

Outputs
-------
data/processed/labeling_readiness.csv
data/processed/labeling_summary.csv
data/processed/modeling_dataset.csv      (header only; no invented rows)
reports/tables/label_specification.md
reports/tables/feasibility_report.md

Run after extract_incidents.py, clean_data.py and match_environmental_data.py:
    .venv\\Scripts\\python.exe python\\prepare_labels.py
"""

from __future__ import annotations

from collections import Counter
from datetime import date

from common import (
    PROCESSED_DIR,
    TABLE_DIR,
    ensure_dirs,
    read_csv,
    text,
    write_csv,
)

MODEL_COLUMNS = [
    "observation_id",
    "event_id",
    "event_group",
    "station_name",
    "reported_lake_zone",
    "observation_timestamp",
    "dissolved_oxygen_mg_l",
    "water_temperature_c",
    "ph",
    "nitrate_mg_l",
    "phosphate_mg_l",
    "bod_mg_l",
    "rainfall_mm_24h",
    "wind_speed_ms",
    "fish_kill_within_24h",
    "label_status",
    "source_ids",
]


def parse_date(value: str) -> date | None:
    try:
        return date.fromisoformat(text(value))
    except ValueError:
        return None


def main() -> None:
    ensure_dirs()
    events = read_csv(PROCESSED_DIR / "historical_fish_kill_events.csv")
    lake = read_csv(PROCESSED_DIR / "water_quality_lake_annual.csv")
    wq_long = read_csv(PROCESSED_DIR / "water_quality_long.csv")
    weather = read_csv(PROCESSED_DIR / "weather_monthly_wide.csv")
    matches = read_csv(PROCESSED_DIR / "incident_environmental_matches.csv")

    event_dates = [parse_date(event["event_start_date"]) for event in events]
    event_dates = [value for value in event_dates if value]
    event_years = {value.year for value in event_dates}
    event_periods = {event["event_start_date"][:7] for event in events if event["event_start_date"]}
    zones = {text(event["lake_zone"]) for event in events if text(event["lake_zone"])}
    complete_lake = sum(1 for row in lake if row["all_six_reported"] == "yes")
    lake_station_years = len(lake)
    non_event_station_years = sum(
        1 for row in lake if str(row.get("year", "")) not in {str(year) for year in event_years}
    )
    daily_rows = sum(
        1 for row in wq_long
        if len(text(row.get("observation_timestamp", ""))) >= 10
    )
    numeric_wq = sum(
        1 for row in wq_long
        if text(row.get("value", "")) and row.get("quality_flag") in {"ok", "out_of_range"}
    )
    numeric_weather = sum(
        1 for row in weather
        if text(row.get("rainfall_mm", "")) or text(row.get("wind_speed_ms", ""))
    )
    pre_event_matches = sum(
        1 for row in matches
        if row["temporal_relation"] == "before_event"
        and row["usable_as_pre_event_predictor"] == "yes"
    )
    station_coords = 0
    zone_mapped = sum(1 for row in lake if text(row.get("reported_lake_zone", "")))
    zone_mapped_stations = len({
        row["station_name"] for row in lake if text(row.get("reported_lake_zone", ""))
    })

    checks = [
        {
            "check_id": "L1",
            "requirement": "At least two independent documented event periods for a chronological split",
            "status": "fail" if len(event_periods) < 2 else "pass",
            "evidence": f"{len(event_periods)} event period(s); {len(events)} accepted report(s); event years {sorted(event_years)}",
            "consequence": "Cannot place events in both training and test periods.",
        },
        {
            "check_id": "L2",
            "requirement": "Independently corroborated event records",
            "status": "fail" if len(events) == 0 else "partial",
            "evidence": "One institutional news report; no second source or formal LLDA/BFAR incident report supplied.",
            "consequence": "Event status is plausible but not independently verified.",
        },
        {
            "check_id": "L3",
            "requirement": "Exact event start date for a 24-hour window",
            "status": "pass" if event_dates else "fail",
            "evidence": "Biñan start 2019-05-04; Pila start 2019-05-12; end only approximate.",
            "consequence": "A start-day window is possible, but only for one event.",
        },
        {
            "check_id": "L4",
            "requirement": "Dated water-quality observations (daily or sub-daily)",
            "status": "fail" if daily_rows == 0 else "pass",
            "evidence": f"{daily_rows} rows have a full observation timestamp; {numeric_wq:,} numeric annual station-year values exist.",
            "consequence": "No pre-event water-quality feature vector can be constructed.",
        },
        {
            "check_id": "L5",
            "requirement": "A pre-event environmental match at a known lead time",
            "status": "pass" if pre_event_matches > 0 else "fail",
            "evidence": f"{pre_event_matches} usable pre-event matches; the article sample is during-event.",
            "consequence": "No observation is known to have been available before the event.",
        },
        {
            "check_id": "L6",
            "requirement": "Documented station coordinates and lake-zone mapping",
            "status": "fail" if station_coords == 0 else "pass",
            "evidence": f"{station_coords} coordinates; {zone_mapped_stations}/15 lake stations have a zone label in their name.",
            "consequence": "Events cannot be assigned to a station or zone defensibly.",
        },
        {
            "check_id": "L7",
            "requirement": "Credible non-event windows with documented incident reporting",
            "status": "fail",
            "evidence": (
                f"{non_event_station_years} annual station-years fall outside {sorted(event_years)}, "
                "but there is no incident-reporting log to establish that no fish kill occurred."
            ),
            "consequence": "Absence of a published report cannot be treated as a negative label.",
        },
        {
            "check_id": "L8",
            "requirement": "Enough events for class-imbalance-aware evaluation",
            "status": "fail",
            "evidence": "1 event period; no 24-hour negatives; class balance cannot be estimated.",
            "consequence": "Precision, recall and F1 would be undefined or meaningless.",
        },
        {
            "check_id": "L9",
            "requirement": "A 24-hour prediction horizon supported by sampling frequency",
            "status": "fail",
            "evidence": "Water quality is annual; weather is monthly. Neither resolves 24 hours.",
            "consequence": "The proposed 24-hour target is not supported.",
        },
        {
            "check_id": "L10",
            "requirement": "Sufficient independent observations for chronological validation and a held-out period",
            "status": "fail",
            "evidence": "One event period, one location pair, one event year.",
            "consequence": "No honest train/validation/test evaluation is possible.",
        },
    ]
    write_csv(PROCESSED_DIR / "labeling_readiness.csv", checks)

    summary = [
        {"metric": "accepted_event_records", "value": len(events)},
        {"metric": "independent_event_periods", "value": len(event_periods)},
        {"metric": "independently_verified_events", "value": 0},
        {"metric": "event_years", "value": ";".join(str(year) for year in sorted(event_years))},
        {"metric": "usable_24h_positive_labels", "value": 0},
        {"metric": "usable_24h_negative_labels", "value": 0},
        {"metric": "lake_station_years", "value": lake_station_years},
        {"metric": "complete_six_variable_lake_station_years", "value": complete_lake},
        {"metric": "annual_station_years_outside_event_year", "value": non_event_station_years},
        {"metric": "dated_water_quality_rows", "value": daily_rows},
        {"metric": "numeric_annual_water_quality_values", "value": numeric_wq},
        {"metric": "numeric_monthly_weather_rows", "value": numeric_weather},
        {"metric": "pre_event_predictive_matches", "value": pre_event_matches},
        {"metric": "station_coordinates", "value": station_coords},
        {"metric": "lake_stations_with_zone_label", "value": zone_mapped_stations},
        {"metric": "label_generation_status", "value": "blocked"},
    ]
    write_csv(PROCESSED_DIR / "labeling_summary.csv", summary)

    # Header-only schema. No synthetic rows and no labels.
    write_csv(PROCESSED_DIR / "modeling_dataset.csv", [], MODEL_COLUMNS)

    label_spec = """# Label specification (NOT ACTIVE)

## Status

**Blocked.** No `fish_kill_within_24h` value has been generated. The data do not
support it: LLDA water quality is annual, PAGASA weather is monthly, and there
is one event period with no pre-event dated observation.

## Target definition if the data ever support it

- **Unit of analysis:** one station-zone observation at a known timestamp `t`.
- **Prediction timestamp:** `t` (the moment the observation and any then-available
  weather inputs are known). No future value may enter the feature vector.
- **Horizon:** `(t, t + 24 hours]`.
- **Positive:** `fish_kill_within_24h = 1` if a documented incident *starts* in
  the same lake zone during the 24-hour window, or if the zone is already under
  a verified incident at `t` (an ongoing event is a positive). The event must
  have at least day precision.
- **Negative:** `0` only when a dated incident-reporting log covers the same
  zone and window and records no incident, and the observation itself passes
  quality control. A blank news archive is not a negative.
- **Ambiguous:** exclude when the event date is only a month/year, when the
  location cannot be assigned to the zone, or when reporting completeness is
  unknown.
- **Overlapping/duplicate reports:** collapse reports describing the same event
  (same zone and overlapping dates after source review); a single event
  contributes one positive window per prediction timestamp, not one per article.
- **Lead-time audit:** record the source timestamp of every feature and prove it
  was available at `t`.

## Why this cannot be applied now

| Required input | Current state |
|---|---|
| Dated water-quality observations | Annual station summaries only |
| Event dates | One event period (May 2019), start days for two municipalities |
| Event-to-zone mapping | No zone label or coordinates |
| Credible negatives | No incident-reporting log |
| 24-hour weather | Monthly summaries only |
| Enough events | One period, no held-out period |

## What must be obtained

1. LLDA/BFAR dated fish-kill incident log (event start/end, site, zone, source).
2. LLDA dated water-quality observations (at least daily; hourly preferable).
3. PAGASA daily or hourly rainfall/wind for a station linked to each zone.
4. Station coordinates and an authoritative lake-zone boundary map.
5. A documented reporting-completeness record so negatives are credible.

The target and window must be re-approved after those data are inspected. A
48-hour or 72-hour target would require an even longer, complete time series.
"""
    (TABLE_DIR / "label_specification.md").write_text(label_spec, encoding="utf-8")

    lines = [
        "# HIMPIL feasibility report",
        "",
        "Generated by `python/prepare_labels.py` from the inspected source files.",
        "",
        "## Bottom line",
        "",
        "**Real-data supervised machine learning is not currently feasible.** No real-data",
        "classifier was trained, no real prediction was generated, and no real performance metric",
        "exists. The blocker is evidence, not software. A separate synthetic base dataset and a",
        "synthetic prototype exist for software demonstration only; neither is evidence or changes",
        "this verdict.",
        "",
        "## Phase 2-4 evidence counts",
        "",
        "| Item | Count / status |",
        "|---|---|",
        f"| Accepted event reports | {len(events)} (May 2019, Biñan and Pila) |",
        f"| Unique event periods | {len(event_periods)} |",
        "| Independently verified events | 0 |",
        "| Official investigation reports | 0 |",
        f"| Usable 24-hour positive labels | 0 |",
        f"| Usable 24-hour negative labels | 0 |",
        f"| Lake station-years | {lake_station_years} (15 stations x 10 years) |",
        f"| Complete across six variables | {complete_lake} |",
        f"| Dated station-monitoring water-quality rows | {daily_rows} |",
        f"| Pre-event predictive matches | {pre_event_matches} |",
        "| Class imbalance | Not estimable |",
        "| Real model metrics | None (no real model; synthetic artifacts are separate) |",
        "",
        "A single event report is not a training dataset. The 135 annual lake station-years outside",
        "2019 cannot be called non-events because no incident-reporting log establishes absence.",
        "",
        "## Data compatibility matrix",
        "",
        "| Source | Resolution | Geographic key | Can be joined to the 2019 event? | Valid ML use |",
        "|---|---|---|---|---|",
        "| LLDA water-quality workbooks (S02-S07) | Annual station summary | Station name; 5 of 15 stations have a bay name | Only as annual context for 2019 | Descriptive analysis only |",
        "| PAGASA rainfall (S01) | Monthly station total | Station name; no coordinates | Month overlaps, station does not | Descriptive analysis only |",
        "| PAGASA wind (S08) | Monthly station value | Station name; no coordinates | Month overlaps, station does not | Descriptive analysis only |",
        "| UPD 2019 article (S14) | One event + one sample | Municipality | Yes, descriptive | Event record and during-event context |",
        "| Sustainability review (S10) | Aggregate table/narrative | Lake | No individual Laguna event | Background/evidence audit |",
        "| AWQR 2009-2012 (S09) | Annual station summaries | Station | Outside 2016-2025 and annual | Background only |",
        "",
        "## Phase 5: is 24-hour prediction supported?",
        "",
        "**No.** A 24-hour label requires dated observations at least daily and event times with at",
        "least day precision. The water-quality workbooks contain one annual value per station-year.",
        "The weather workbooks contain one value per station-month. The article provides one",
        "during-event sample. The 24-hour target is therefore undefined for almost every row.",
        "",
        "A 48-hour or 72-hour target is equally unsupported. Moving to an annual target would not",
        "rescue the model: there is still only one event year and no credible negative reporting.",
        "",
        "## Why the single event cannot be used as a case study model",
        "",
        "- One event cannot be split chronologically into training and test periods.",
        "- There is no pre-event feature vector at a known lead time.",
        "- The two municipalities do not have a documented lake-zone or station mapping.",
        "- The article reports loss estimates and percentages, not a complete event census.",
        "- Repeating the event across its four weeks or two municipalities would create leakage.",
        "",
        "## What can be done now, honestly",
        "",
        "1. Describe annual water-quality conditions and trends (Python and R).",
        "2. Describe monthly rainfall and wind seasonality (Python and R).",
        "3. Show data coverage, missingness and station continuity.",
        "4. Present the sourced 2019 event as a case narrative, not as a model result.",
        "5. Show a dashboard with an explicit 'risk assessment unavailable' state.",
        "",
        "## Evaluation design for later (not executed)",
        "",
        "- Sort observations by timestamp, never randomly.",
        "- Use an earlier training period, a later validation period, and a final untouched test period.",
        "- Group all rows from one event and adjacent windows into the same split to prevent leakage.",
        "- Compare a majority-class baseline with a Decision Tree and a Random Forest.",
        "- Report precision, recall, F1, confusion matrix and precision-recall AUC.",
        "- Inspect false alarms and missed events separately.",
        "- Report the event count and confidence intervals, not only point estimates.",
        "",
        "## Required next data",
        "",
        "1. LLDA/BFAR dated fish-kill incident log with site, zone, start/end, losses and cause.",
        "2. LLDA dated water-quality observations (daily or better).",
        "3. PAGASA daily rainfall, wind and air temperature linked to a documented station.",
        "4. Station coordinates and lake-zone boundaries.",
        "5. A reporting-completeness record for negative windows.",
        "",
        "See `label_specification.md` for the exact target that would be used after those data arrive.",
        "",
        "> A quarantined synthetic prototype exists in `sandbox/synthetic/` for software",
        "> demonstration only. It is labeled **SIMULATION ONLY — NOT EVIDENCE**, does not",
        "> satisfy this report's gate, and does not change the real-data verdict above.",
    ]
    (TABLE_DIR / "feasibility_report.md").write_text("\n".join(lines), encoding="utf-8")

    print("Label readiness assessment complete")
    print(f"Accepted events       : {len(events)}")
    print(f"Event periods         : {len(event_periods)}")
    print(f"Label status          : blocked")
    print(f"24h positive labels   : 0")
    print(f"24h negative labels   : 0")
    print(f"Readiness checks      : {Counter(row['status'] for row in checks)}")
    print(f"Report                : {TABLE_DIR / 'feasibility_report.md'}")


if __name__ == "__main__":
    main()
