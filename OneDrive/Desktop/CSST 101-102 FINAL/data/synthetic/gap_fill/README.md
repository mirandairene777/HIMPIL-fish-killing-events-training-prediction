# HIMPIL synthetic gap-filled database

This is a synthetic, end-to-end training database built from the supplied LLDA
annual water-quality summaries, PAGASA monthly weather summaries, and the
existing synthetic base panel. It fills the ten training checks in a
**synthetic scope** so the pipeline can be exercised from database to model.

The real evidence gate is unchanged. This database is separate from
`dashboard/src/data/dashboard.json` and must not be used for a real advisory.

## What was filled

| Gap | Synthetic resolution |
|---|---|
| Dated water-quality observations | 54,795 synthetic station-days, including 400 dated pre-event rows |
| At least two exact-dated event periods | 20 synthetic fish-kill events across 10 years |
| Documented incident reports | 30 incident/patrol records |
| Credible non-event windows | 1,700 monthly patrol windows with zero fish-kill reports |
| Station coordinates | 15 synthetic station coordinates |
| Authoritative zone crosswalk | 15 station-to-zone assignments |
| Per-station annual aggregation rule | 15 station rules |
| Independent event corroboration | 40 synthetic corroboration records |

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
.\.venv\Scripts\python.exe sandbox\synthetic\build_gap_filled_database.py
.\.venv\Scripts\python.exe sandbox\synthetic\train_gap_filled_model.py
```

The generator is deterministic by default. Every table carries
`data_origin = synthetic_gap_fill_v1`.
