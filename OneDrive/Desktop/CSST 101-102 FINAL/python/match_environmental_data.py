"""
HIMPIL Phase 3b - match documented incidents to environmental observations.

The matching is temporal and geographic, not merely a join on year. A monthly
weather value that covers the event month is not a same-day observation. A
water sample collected during or after an event is not a pre-event predictor.

Outputs
-------
data/processed/incident_environmental_matches.csv
data/processed/matching_summary.csv
reports/tables/matching_report.md

Run after extract_incidents.py and clean_data.py:
    .venv\\Scripts\\python.exe python\\match_environmental_data.py
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


def parse_date(value: str) -> date | None:
    value = text(value)
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def main() -> None:
    ensure_dirs()
    events = read_csv(PROCESSED_DIR / "historical_fish_kill_events.csv")
    context = read_csv(PROCESSED_DIR / "incident_context_measurements.csv")
    lake = read_csv(PROCESSED_DIR / "water_quality_lake_annual.csv")
    weather = read_csv(PROCESSED_DIR / "weather_monthly_wide.csv")

    context_by_event = {}
    for row in context:
        context_by_event.setdefault(row["event_id"], []).append(row)

    matches = []
    for event in events:
        event_id = event["event_id"]
        start = parse_date(event["event_start_date"])
        end = parse_date(event["event_end_date"])
        year = start.year if start else ""

        # 1. The article's own sample. It is a genuine geographic match but it
        # was collected during the event, so it cannot be a predictor.
        for observation in context_by_event.get(event_id, []):
            obs_date = parse_date(observation["measurement_date"])
            if start and end and obs_date and start <= obs_date <= end:
                relation = "during_event"
            elif start and obs_date and obs_date < start:
                relation = "before_event"
            else:
                relation = "after_event"
            matches.append({
                "event_id": event_id,
                "event_start_date": event["event_start_date"],
                "event_location": event["location"],
                "environment_source": "S14 - UPD article, Table 1",
                "observation_period": observation["measurement_date"],
                "observation_location": observation["location"],
                "variables": observation["variable"],
                "temporal_relation": relation,
                "geographic_match": "same municipality (Biñan)",
                "temporal_resolution": "single sample",
                "usable_as_pre_event_predictor": "no",
                "reason": (
                    "Sample was collected during/at the end of the reported event; "
                    "it is descriptive context, not a pre-event input."
                ),
            })

        # 2. LLDA annual lake summaries. The 2019 row covers the event year,
        # but the observation date and the aggregation rule are unknown.
        lake_year_rows = [row for row in lake if str(row.get("year", "")) == str(year)]
        if lake_year_rows:
            numeric = sum(int(row["variables_reported"]) for row in lake_year_rows)
            matches.append({
                "event_id": event_id,
                "event_start_date": event["event_start_date"],
                "event_location": event["location"],
                "environment_source": "S02-S07 - LLDA annual water-quality workbooks",
                "observation_period": f"{year} annual summary",
                "observation_location": f"{len(lake_year_rows)} lake stations (no event-zone match)",
                "variables": "Nitrate, phosphate, BOD, pH, water temperature, DO (where reported)",
                "temporal_relation": "annual_period_contains_event",
                "geographic_match": "lake-wide only; no Biñan/Pila station and no coordinates",
                "temporal_resolution": "annual station summary",
                "usable_as_pre_event_predictor": "no",
                "reason": (
                    "The source gives one annual value per station-year. It does not reveal whether "
                    "the value precedes the May 2019 event, and it cannot identify a 24-hour window. "
                    f"{numeric} numeric station-variable values exist for {year}, but none is a dated observation."
                ),
            })

        # 3. PAGASA monthly data. May 2019 is present, but no station is linked
        # to Biñan/Pila and no coordinates are supplied.
        event_month = start.month if start else ""
        month_rows = [
            row for row in weather
            if str(row.get("year", "")) == str(year)
            and str(row.get("month_number", "")) == str(event_month)
        ]
        if month_rows:
            rainfall_numeric = sum(1 for row in month_rows if text(row.get("rainfall_mm", "")))
            wind_numeric = sum(1 for row in month_rows if text(row.get("wind_speed_ms", "")))
            matches.append({
                "event_id": event_id,
                "event_start_date": event["event_start_date"],
                "event_location": event["location"],
                "environment_source": "S01/S08 - PAGASA monthly rainfall and wind",
                "observation_period": f"{year}-{int(event_month):02d} (monthly summary)",
                "observation_location": (
                    f"{len(month_rows)} weather-station rows; none named Biñan or Pila; no coordinates"
                ),
                "variables": f"Rainfall ({rainfall_numeric} numeric), wind speed ({wind_numeric} numeric)",
                "temporal_relation": "monthly_period_contains_event",
                "geographic_match": "not established; no station-to-lake-zone mapping",
                "temporal_resolution": "monthly station summary",
                "usable_as_pre_event_predictor": "no",
                "reason": (
                    "The monthly value is not a daily measurement, and the source does not establish "
                    "which PAGASA station represents Biñan or Pila."
                ),
            })

    write_csv(PROCESSED_DIR / "incident_environmental_matches.csv", matches)

    total_events = len(events)
    context_matches = sum(1 for row in matches if row["environment_source"].startswith("S14"))
    context_events = len({row["event_id"] for row in matches if row["environment_source"].startswith("S14")})
    pre_event_matches = sum(
        1 for row in matches
        if row["temporal_relation"] == "before_event"
        and row["usable_as_pre_event_predictor"] == "yes"
    )
    predictive_matches = sum(1 for row in matches if row["usable_as_pre_event_predictor"] == "yes")
    zones = sum(1 for event in events if text(event.get("lake_zone", "")))
    summary = [
        {"metric": "accepted_event_records", "value": total_events, "note": "One report, two municipalities, May 2019"},
        {"metric": "unique_event_periods", "value": len({event["event_start_date"][:7] for event in events}), "note": "May 2019"},
        {"metric": "events_with_exact_start_date", "value": sum(1 for event in events if event["event_start_date"]), "note": ""},
        {"metric": "events_with_lake_zone", "value": zones, "note": "No zone label in the source"},
        {"metric": "events_with_any_matched_observation", "value": context_events, "note": "Article sample only"},
        {"metric": "events_with_pre_event_environmental_observation", "value": pre_event_matches, "note": "No dated pre-event water-quality observation"},
        {"metric": "predictive_matches_usable_now", "value": predictive_matches, "note": "No row is usable as a pre-event predictor"},
        {"metric": "daily_water_quality_observations", "value": 0, "note": "All LLDA workbooks are annual summaries"},
        {"metric": "station_coordinates_available", "value": 0, "note": "No coordinates in any supplied file"},
    ]
    write_csv(PROCESSED_DIR / "matching_summary.csv", summary)

    lines = [
        "# Incident-to-environment matching report",
        "",
        "Generated by `python/match_environmental_data.py`.",
        "",
        "## Headline",
        "",
        f"- Accepted event records: **{total_events}** (one event report, two municipalities).",
        "- Unique event periods: **1** (May 2019).",
        "- Events with a matched, **pre-event** environmental observation: **0**.",
        "- Events with a lake-zone label: **0**.",
        "- Environmental matches usable as predictors now: **0**.",
        "",
        "## What did match",
        "",
        "The UPD article's 29 May 2019 Biñan sample matches the event municipality and falls "
        "inside the reported event period. It is a **during-event** observation, not a "
        "pre-event predictor. The article reports DO 4.7 mg/L, ammonia 0.16 mg/L, nitrate "
        "0.4 mg/L and phosphate 1.00 mg/L.",
        "",
        "The LLDA 2019 annual lake summaries overlap the event year but have no observation "
        "dates, no Biñan/Pila station and no aggregation rule. They cannot establish what was "
        "known before 4 May 2019. The PAGASA May 2019 monthly summaries also overlap the event "
        "month, but no weather station is linked to the event location and no coordinates exist.",
        "",
        "## Why the remaining event is unmatched for prediction",
        "",
        "| Requirement | Result | Consequence |",
        "|---|---|---|",
        "| Exact event start | Present (4 May 2019; Pila 12 May) | Could define an event timestamp |",
        "| Exact pre-event observation | None | No features at a known lead time |",
        "| Daily or sub-daily water quality | None | 24-hour target cannot be observed |",
        "| Station coordinates / zone map | None | Cannot spatially link stations to Biñan/Pila |",
        "| Representative PAGASA station | Not documented | Monthly weather cannot be assigned to the event site |",
        "| Independent event corroboration | None in supplied files | Verification remains limited |",
        "",
        "## Sampling-frequency mismatch",
        "",
        "- LLDA water quality: one aggregated value per station-year (underlying sampling may have been monthly, but dates are not published in the supplied workbooks).",
        "- PAGASA rainfall/wind: one value per station-month; 2025 is partial and provisional.",
        "- The 2019 event lasted about four weeks. An annual summary cannot resolve a 24-hour warning window.",
        "",
        "## Geographic mismatch",
        "",
        "- The event is reported at Biñan and Pila, Laguna. No LLDA lake station is labelled Biñan or Pila.",
        "- Five lake stations carry an explicit bay name (West, East, Central, South); ten do not and no coordinates are supplied.",
        "- The PAGASA roster contains no Biñan or Pila station. Without coordinates, any 'nearest station' choice would be an assumption, not a documented match.",
        "",
        "## Temporal ordering (never use the future as a predictor)",
        "",
        "- Article sample: **during_event** -> descriptive only.",
        "- Annual LLDA 2019 values: **period contains event** -> not a pre-event measurement.",
        "- Monthly PAGASA May 2019 values: **period contains event** -> not a daily pre-event measurement.",
        "",
        "## Unmatched incidents",
        "",
        "All accepted event records lack a usable pre-event environmental match. The review's "
        "1972-1998 aggregate and its contradictory 2021 row remain excluded (see "
        "`incident_evidence_audit.csv`).",
        "",
        "## Minimum data needed for a real match",
        "",
        "1. LLDA sampling dates and values (not annual averages), or an official dated observation log.",
        "2. Incident dates with at least the start day and a precise site.",
        "3. Station coordinates and an authoritative lake-zone boundary map.",
        "4. A documented rule for assigning a station or zone to an incident.",
        "5. Enough events to create both event and credible non-event windows.",
    ]
    (TABLE_DIR / "matching_report.md").write_text("\n".join(lines), encoding="utf-8")

    print("Matching audit complete")
    print(f"Accepted events: {total_events}")
    print(f"Context observation rows: {context_matches}")
    print(f"Events with a matched observation: {context_events}")
    print("Pre-event predictive matches: 0")
    print(f"Output: {PROCESSED_DIR / 'incident_environmental_matches.csv'}")


if __name__ == "__main__":
    main()
