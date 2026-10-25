"""
HIMPIL Phase 2 - extract documented fish kill incidents.

The extraction is deliberately conservative:

* An aggregate statement ("fish kills occurred in 1972-1998") is not expanded
  into invented events.
* A table row is rejected when its own citation points to a different lake.
* A single dated institutional news report is retained as one reported event,
  with its verification limits recorded.

Outputs
-------
data/processed/historical_fish_kill_events.csv
data/processed/incident_evidence_audit.csv
data/processed/incident_context_measurements.csv
reports/tables/incident_extraction_report.md

Run from the project root:
    .venv\\Scripts\\python.exe python\\extract_incidents.py
"""

from __future__ import annotations

from common import (
    EVENT_COLUMNS,
    PROCESSED_DIR,
    TABLE_DIR,
    ensure_dirs,
    write_csv,
)

UPD_URL = (
    "https://upd.edu.ph/seasonal-fish-kill-incident-leaves-thousands-of-"
    "unprofitable-commodity-fish-in-laguna-de-bay/"
)

EVENTS = [
    {
        "event_id": "HIMPIL-FK-2019-001",
        "event_start_date": "2019-05-04",
        "event_end_date": "2019-05-31",
        "location": "Biñan and Pila, Laguna (Laguna de Bay)",
        "municipality": "Biñan; Pila",
        "lake_zone": "",
        "fish_species": "Tilapia; bangus (milkfish)",
        "estimated_fish_losses": (
            "Approximately 500,000 fish reported dead in fish cages in Biñan "
            "(fisherman's estimate); in Barangay Linga, Pila, 60% of tilapia and "
            "80% of bangus in cages were reported killed. No complete count."
        ),
        "estimated_economic_loss": "",
        "reported_cause": (
            "Green tide (freshwater algal bloom) causing oxygen deficiency/asphyxia; "
            "attributed to an LLDA senior science research specialist quoted in the article."
        ),
        "source_title": (
            "Seasonal Fish Kill Incident Leaves Thousands of Unprofitable Commodity "
            "Fish in Laguna de Bay"
        ),
        "source_url": UPD_URL,
        "publication_date": "2019-06-10",
        "date_precision": (
            "Start dates exact for Biñan (4 May) and Pila (12 May); end date only "
            "described as 'until the end of May', so 31 May is an approximate boundary."
        ),
        "location_precision": (
            "Municipality-level for Biñan and Pila; one site named as Barangay Linga, Pila. "
            "No coordinates or lake-zone label are provided."
        ),
        "verification_status": (
            "Single institutional news report (UP Diliman) with named LLDA attribution "
            "and a water-quality table; not a formal LLDA investigation report and not "
            "independently corroborated in the supplied files."
        ),
        "notes": (
            "One article reports a fish kill across two municipalities during overlapping "
            "periods; it is retained as one event to avoid double-counting. The article's "
            "water sample was collected on 29 May 2019 (during/near the end of the event), "
            "not before it. Byline date is 10 June 2019; the page also shows a 13 June "
            "dateline. No peso loss or lake-zone designation is reported."
        ),
    }
]

AUDIT = [
    {
        "candidate_id": "CAND-01",
        "claim": "Fish kills in Laguna de Bay were reported in the 1930s.",
        "source_id": "S10",
        "source_locator": "Section 2.2, narrative paragraph",
        "issue": "No year, month, date, location within the lake, count, loss, or cause.",
        "decision": "excluded",
        "reason": "Cannot form an event record or a label.",
    },
    {
        "candidate_id": "CAND-02",
        "claim": (
            "From 1972 to 1998, 60% of Laguna de Bay fish-kill incidents were due to low "
            "dissolved oxygen; 80% occurred in May-September, mostly in the central arm "
            "and then the west arm."
        ),
        "source_id": "S10",
        "source_locator": "Section 2.2 and Table 3",
        "issue": "Aggregate statistics over 27 years; no individual event dates, counts, or losses.",
        "decision": "excluded",
        "reason": "Aggregate statements must not be converted into invented event rows.",
    },
    {
        "candidate_id": "CAND-03",
        "claim": "Table 3 lists '2021 Jan. Laguna de Bay / Tilapia / Low DO levels [121]'.",
        "source_id": "S10",
        "source_locator": "Table 3, page 9",
        "issue": (
            "The row's cited source [121] is titled '2 Tons of Tilapia Lost as Fish Kill "
            "Hits Laguna's Sampaloc Lake'. Sampaloc Lake is a different waterbody."
        ),
        "decision": "excluded_pending_verification",
        "reason": "The table row and its citation conflict; do not count it as Laguna de Bay.",
    },
    {
        "candidate_id": "CAND-04",
        "claim": (
            "Massive fish kill in Biñan and Pila, Laguna, starting 4 May and 12 May 2019, "
            "respectively, lasting until the end of May."
        ),
        "source_id": "S14",
        "source_locator": "Article body and Table 1",
        "issue": (
            "One secondary source; two municipalities in one report; end date approximate; "
            "no lake-zone label or coordinates; environmental sample collected during event."
        ),
        "decision": "accepted_as_reported_event",
        "reason": "Meets the minimum for a dated, located event record; verification limits are recorded.",
    },
]

CONTEXT_MEASUREMENTS = [
    {
        "event_id": "HIMPIL-FK-2019-001",
        "measurement_date": "2019-05-29",
        "location": "Biñan, Laguna",
        "variable": "Dissolved oxygen",
        "value": "4.7",
        "unit": "mg/L",
        "comparison_reported": "5.0 mg/L DAO 2016-08 limit",
        "temporal_relation_to_event": "during_event",
        "source_id": "S14",
        "notes": "UPD-IESM/LLDA sampling reported in the article; not a pre-event measurement.",
    },
    {
        "event_id": "HIMPIL-FK-2019-001",
        "measurement_date": "2019-05-29",
        "location": "Biñan, Laguna",
        "variable": "Ammonia",
        "value": "0.16",
        "unit": "mg/L",
        "comparison_reported": "0.05 mg/L DAO 2016-08 limit",
        "temporal_relation_to_event": "during_event",
        "source_id": "S14",
        "notes": "UPD-IESM/LLDA sampling reported in the article; not a pre-event measurement.",
    },
    {
        "event_id": "HIMPIL-FK-2019-001",
        "measurement_date": "2019-05-29",
        "location": "Biñan, Laguna",
        "variable": "Nitrate",
        "value": "0.4",
        "unit": "mg/L",
        "comparison_reported": "7.0 mg/L DAO 2016-08 limit",
        "temporal_relation_to_event": "during_event",
        "source_id": "S14",
        "notes": "UPD-IESM/LLDA sampling reported in the article; not a pre-event measurement.",
    },
    {
        "event_id": "HIMPIL-FK-2019-001",
        "measurement_date": "2019-05-29",
        "location": "Biñan, Laguna",
        "variable": "Phosphate",
        "value": "1.00",
        "unit": "mg/L",
        "comparison_reported": "0.5 mg/L DAO 2016-08 limit",
        "temporal_relation_to_event": "during_event",
        "source_id": "S14",
        "notes": "UPD-IESM/LLDA sampling reported in the article; not a pre-event measurement.",
    },
]


def write_report() -> None:
    lines = [
        "# Fish-kill incident extraction report",
        "",
        "Generated by `python/extract_incidents.py`.",
        "",
        "## Result",
        "",
        f"- Accepted event records: **{len(EVENTS)}**",
        "- Event periods: **1** (one report covering Biñan and Pila, May 2019)",
        "- Independently verified events in the supplied files: **0**",
        "- Events with a complete loss count or peso value: **0**",
        "- Events with a documented lake-zone label: **0**",
        "",
        "The single accepted record is a reported event with named locations and dates. It is not a",
        "formal investigation report, and it is not enough for model training.",
        "",
        "## Evidence audit",
        "",
        "| Candidate | Claim | Decision | Reason |",
        "|---|---|---|---|",
    ]
    for row in AUDIT:
        lines.append(
            f"| {row['candidate_id']} | {row['claim'].replace('|', '/')} | "
            f"{row['decision']} | {row['reason'].replace('|', '/')} |"
        )
    lines += [
        "",
        "## Important exclusions",
        "",
        "1. The 1972-1998 Laguna statement is an aggregate. It was not expanded into 27 years of",
        "   invented events.",
        "2. The review's 2021 row is not accepted because its citation is about Sampaloc Lake.",
        "   The row may be a transcription error in the review; an original LLDA advisory or",
        "   incident report would be needed to resolve it.",
        "3. The 2019 article reports one event across two municipalities. It is stored as one",
        "   event to avoid double-counting overlapping reports.",
        "",
        "## What would raise the evidence standard",
        "",
        "- An LLDA or BFAR incident log with event dates, sites, species, losses and causes.",
        "- Independent corroboration of the 2019 event and any other event.",
        "- Official lake-zone boundaries and station coordinates.",
        "- Monthly or daily LLDA water-quality observations with dates (not annual averages).",
        "",
        "## Files",
        "",
        "- `data/processed/historical_fish_kill_events.csv` - accepted event record(s).",
        "- `data/processed/incident_evidence_audit.csv` - accepted and rejected evidence.",
        "- `data/processed/incident_context_measurements.csv` - article's 29 May 2019 sample.",
    ]
    (TABLE_DIR / "incident_extraction_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    ensure_dirs()
    write_csv(PROCESSED_DIR / "historical_fish_kill_events.csv", EVENTS, EVENT_COLUMNS)
    write_csv(PROCESSED_DIR / "incident_evidence_audit.csv", AUDIT)
    write_csv(PROCESSED_DIR / "incident_context_measurements.csv", CONTEXT_MEASUREMENTS)
    write_report()
    print(f"Accepted event records: {len(EVENTS)}")
    print(f"Event periods: {len({row['event_start_date'][:7] for row in EVENTS})}")
    print("Independently verified events: 0 (no second source supplied)")
    print(f"Output: {PROCESSED_DIR / 'historical_fish_kill_events.csv'}")


if __name__ == "__main__":
    main()
