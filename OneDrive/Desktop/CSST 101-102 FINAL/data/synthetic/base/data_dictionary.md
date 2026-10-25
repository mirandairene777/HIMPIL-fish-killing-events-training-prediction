# Synthetic base data dictionary

> **SIMULATION ONLY - NOT EVIDENCE**

This folder contains a synthetic daily base dataset. It is **not** evidence about
Laguna de Bay. The station labels, source years, variables, and units come from
the project's real source inventory; the daily values do not.

## Tables

| File | Rows | Description |
|---|---:|---|
| `stations.csv` | 15 | Real lake station labels and supplied zone metadata. No coordinates or measurements are added. |
| `calibration_anchors.csv` | 900 | Real annual station-year anchors where available; synthetic station/network imputations are flagged. |
| `water_quality_daily.csv` | 54795 | Synthetic daily water-quality values for 15 lake stations, 2016-2025. |
| `weather_daily.csv` | 10959 | Synthetic daily weather for three synthetic weather zones. |
| `himpil_synthetic_base.sqlite` | - | SQLite database containing the tables above plus a long-format view and metadata. |

## Daily water-quality columns

| Column | Unit / values | Description |
|---|---|---|
| `station_id` | stable synthetic key | `LAG-LAKE-01` to `LAG-LAKE-15`; maps to the real station label. |
| `station_name` | text | Exact lake station label from the supplied LLDA workbooks. |
| `station_type` | `lake` | All rows are lake stations. |
| `reported_lake_zone` | text or blank | Zone only where the real station label states one. Blank means not supplied. |
| `date` | `YYYY-MM-DD` | Synthetic daily calendar date. |
| `nitrate_mg_l` | mg/L | Synthetic daily nitrate. |
| `phosphate_mg_l` | mg/L | Synthetic daily phosphate. |
| `bod_mg_l` | mg/L | Synthetic daily biochemical oxygen demand. |
| `ph` | pH units | Synthetic daily pH. |
| `water_temp_c` | deg C | Synthetic daily water temperature. |
| `do_mg_l` | mg/L | Synthetic daily dissolved oxygen. |
| `quality_flag` | `synthetic_ok` | Every daily water-quality row is synthetic. |
| `data_origin` | `synthetic_base_v1` | Quarantine marker. |

## Calibration-anchor columns

| Column | Unit / values | Description |
|---|---|---|
| `station_id`, `station_name` | keys | Station mapping used by the daily table. |
| `year` | 2016-2025 | Calendar year of the annual anchor. |
| `variable`, `variable_key` | text | Variable label and stable key. |
| `anchor_value` | variable unit | Real annual value where present; imputed value where missing. |
| `unit` | text | mg/L, pH units, or deg C. |
| `anchor_status` | text | `real_annual_summary`, `real_annual_summary_2025_completeness_unverified`, `synthetic_station_mean_imputed`, or `synthetic_network_mean_imputed`. |
| `source_flag` | text | Original source missing/quality flag. |
| `source_numeric_value_present` | yes/no | Whether a real numeric annual value existed before imputation. |

## Daily weather columns

| Column | Unit / values | Description |
|---|---|---|
| `weather_zone_id` | synthetic key | `SYN-WX-WEST`, `SYN-WX-CENTRAL`, or `SYN-WX-EAST`. |
| `calibration_source_station` | real PAGASA label | Monthly target source; not a real station-to-lake mapping. |
| `date` | `YYYY-MM-DD` | Synthetic daily date. |
| `rainfall_mm` | mm/day | Synthetic daily rainfall, calibrated to a real nearby monthly summary. |
| `wind_mps` | m/s | Synthetic daily wind speed, calibrated to a real nearby monthly summary. |
| `air_temp_c` | deg C | Synthetic daily air temperature; no real daily air-temperature source was supplied. |
| `rainfall_calibration_status`, `wind_calibration_status` | text | Real monthly summary or synthetic climatology fill. |
| `provisional_2025` | yes/no/synthetic_fill | 2025 source status; `synthetic_fill` means the source had no month value. |
| `data_origin` | `synthetic_base_v1` | Quarantine marker. |

## Calibration method

1. Read the real annual lake station-year summaries in
   `data/processed/water_quality_lake_annual.csv`.
2. For each station-year-variable with a real numeric annual value, generate
   daily values with a seasonal shape and AR(1) noise, then rescale the daily
   series so its annual mean is close to the real annual anchor.
3. If the annual cell is missing, use that station's mean across its available
   years. If the station has no value for the variable, use the lake-network
   mean. These imputations are flagged in `calibration_anchors.csv`.
4. 2025 numeric anchors are retained but marked
   `real_annual_summary_2025_completeness_unverified` because the source does
   not document how many months contributed.
5. Weather is synthesized independently for three synthetic weather zones. The
   monthly rainfall and wind targets are taken from real nearby PAGASA station
   summaries. The mapping is a calibration device, not a real station-to-lake
   mapping. 2025 weather is partial in the source and is flagged.

## Units and missingness

- Nitrate, phosphate, BOD, and DO: mg/L.
- Water temperature and air temperature: degrees Celsius.
- pH: pH units.
- Rainfall: mm/day.
- Wind: m/s.
- The synthetic daily tables are intentionally complete. Missingness is
  represented in `calibration_anchors.csv` through `anchor_status`; it is not
  silently treated as zero.
- The real annual water-temperature cell is missing for **39 station-years**,
  including all 15 in 2017. Those cells are imputed in the anchor table and
  flagged as `synthetic_station_mean_imputed`.
- Ten of the fifteen lake stations have no zone label in the source; their
  `reported_lake_zone` value remains blank.

## What is not included

- No fish-kill labels.
- No real or synthetic event dates tied to a real incident.
- No station coordinates.
- No real daily measurements.
- No tributary stations; the base dataset covers the 15 lake stations.
- No zone assignments beyond the five labels stated in the real station names.
- No model metrics and no risk score.

Do not copy these files into `data/processed/`, do not join them to real station
measurements, and do not load them into the evidence dashboard.
