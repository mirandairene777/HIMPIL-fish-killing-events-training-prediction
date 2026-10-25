# Synthetic gap-filled database report

**Generated (UTC):** 2026-10-24T14:39:37+00:00  
**Database:** `data/synthetic/gap_fill/himpil_synthetic_complete.sqlite`  
**Code:** `sandbox/synthetic/build_gap_filled_database.py`  
**Scope:** synthetic training demonstration

## 1. What was filled

The database starts from the supplied annual and monthly summaries and the
existing synthetic base panel. It adds the missing structure needed to train:

| Blocker | Synthetic resolution |
|---|---|
| No dated water-quality observations | **54,795** station-days; **400** pre-event rows across **20** events |
| Only one event period | **20** exact-dated synthetic events in **10** years |
| No incident reports | **30** incident and patrol records |
| No credible non-event windows | **1,700** monthly patrol windows with zero fish-kill reports |
| No coordinates | **15** synthetic station coordinates |
| No authoritative zone map | **15** station-to-zone assignments |
| No aggregation rule | **15** per-station annual rules plus a zone rule |
| No independent corroboration | **40** synthetic corroboration records |

## 2. Readiness

All **10/10** checks pass in
the synthetic scope. The same table records the real-gate status. The real
evidence gate remains **2 pass,
8 fail**; this database does not change it.

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
