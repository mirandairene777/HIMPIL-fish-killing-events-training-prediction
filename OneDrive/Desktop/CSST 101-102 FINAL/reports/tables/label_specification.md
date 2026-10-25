# Label specification (NOT ACTIVE)

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
