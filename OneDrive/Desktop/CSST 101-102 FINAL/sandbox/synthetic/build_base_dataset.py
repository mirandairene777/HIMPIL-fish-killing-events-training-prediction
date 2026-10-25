"""Build a quarantined synthetic base dataset for HIMPIL.

SIMULATION ONLY - NOT EVIDENCE

This script creates daily synthetic water-quality and weather data for the 15
lake station labels that appear in the supplied LLDA workbooks. The synthetic
daily values are calibrated to the real annual station-year summaries in
``data/processed/water_quality_lake_annual.csv`` where those summaries exist.
Missing annual cells are imputed from the same station's available years, then
from the network mean, and are explicitly flagged.

The real source files are read only. Outputs are written to
``data/synthetic/base/`` and must never be copied into ``data/processed/`` or
loaded into the evidence dashboard.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
PROCESSED = ROOT / "data" / "processed"
DEFAULT_OUTPUT_DIR = ROOT / "data" / "synthetic" / "base"
TABLES = ROOT / "reports" / "tables"

WARNING = "SIMULATION ONLY - NOT EVIDENCE"
DATA_ORIGIN = "synthetic_base_v1"
YEARS = list(range(2016, 2026))
DEFAULT_SEED = 20261023

# Variables are keyed to the real annual-summary columns and units. The
# seasonal amplitudes and AR(1) noise are simulation choices, not findings.
VARIABLE_SPECS = [
    {
        "key": "nitrate",
        "label": "Nitrate",
        "annual_column": "Nitrate",
        "flag_column": "Nitrate__flag",
        "daily_column": "nitrate_mg_l",
        "unit": "mg/L",
        "kind": "multiplicative",
        "season": "wet",
        "amplitude": 0.20,
        "noise_sigma": 0.10,
        "phi": 0.72,
        "bounds": (0.005, 5.0),
        "decimals": 3,
    },
    {
        "key": "phosphate",
        "label": "Phosphate",
        "annual_column": "Phosphate",
        "flag_column": "Phosphate__flag",
        "daily_column": "phosphate_mg_l",
        "unit": "mg/L",
        "kind": "multiplicative",
        "season": "wet",
        "amplitude": 0.16,
        "noise_sigma": 0.09,
        "phi": 0.70,
        "bounds": (0.005, 5.0),
        "decimals": 3,
    },
    {
        "key": "bod",
        "label": "BOD",
        "annual_column": "BOD",
        "flag_column": "BOD__flag",
        "daily_column": "bod_mg_l",
        "unit": "mg/L",
        "kind": "multiplicative",
        "season": "wet",
        "amplitude": 0.12,
        "noise_sigma": 0.08,
        "phi": 0.65,
        "bounds": (0.1, 20.0),
        "decimals": 3,
    },
    {
        "key": "ph",
        "label": "pH",
        "annual_column": "pH",
        "flag_column": "pH__flag",
        "daily_column": "ph",
        "unit": "pH units",
        "kind": "additive",
        "season": "warm",
        "amplitude": 0.03,
        "noise_sigma": 0.025,
        "phi": 0.55,
        "bounds": (5.5, 9.5),
        "decimals": 3,
    },
    {
        "key": "temperature",
        "label": "Water temperature",
        "annual_column": "Water temperature",
        "flag_column": "Water temperature__flag",
        "daily_column": "water_temp_c",
        "unit": "deg C",
        "kind": "additive",
        "season": "warm",
        "amplitude": 1.10,
        "noise_sigma": 0.35,
        "phi": 0.72,
        "bounds": (20.0, 35.0),
        "decimals": 2,
    },
    {
        "key": "do",
        "label": "Dissolved oxygen (DO)",
        "annual_column": "Dissolved oxygen (DO)",
        "flag_column": "Dissolved oxygen (DO)__flag",
        "daily_column": "do_mg_l",
        "unit": "mg/L",
        "kind": "additive",
        "season": "cool",
        "amplitude": 0.35,
        "noise_sigma": 0.22,
        "phi": 0.72,
        "bounds": (0.5, 15.0),
        "decimals": 2,
    },
]

# These are synthetic weather zones. The calibration source is a real PAGASA
# station summary, but no real station-to-lake-zone mapping is claimed.
WEATHER_ZONES = [
    {
        "weather_zone_id": "SYN-WX-WEST",
        "calibration_source_station": "Ambulong, Batangas",
        "air_temp_offset_c": -0.1,
    },
    {
        "weather_zone_id": "SYN-WX-CENTRAL",
        "calibration_source_station": "Tanay, Rizal",
        "air_temp_offset_c": 0.0,
    },
    {
        "weather_zone_id": "SYN-WX-EAST",
        "calibration_source_station": "Tayabas, Quezon",
        "air_temp_offset_c": 0.1,
    },
]


def _relative(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _seasonal_shape(kind: str, day_of_year: np.ndarray) -> np.ndarray:
    """Return a zero-mean seasonal shape for one year."""
    angle = 2.0 * np.pi * (day_of_year.astype(float) - 60.0) / 365.25
    if kind == "warm":
        shape = np.sin(angle)
    elif kind == "cool":
        shape = -np.sin(angle)
    elif kind == "wet":
        wet_angle = 2.0 * np.pi * (day_of_year.astype(float) - 200.0) / 365.25
        shape = np.cos(wet_angle)
    else:
        shape = np.sin(angle)
    shape = np.asarray(shape, dtype=float)
    shape -= shape.mean()
    return shape


def _ar1_noise(
    rng: np.random.Generator, n: int, phi: float, sigma: float
) -> np.ndarray:
    innovations = rng.normal(0.0, sigma, size=n)
    values = np.empty(n, dtype=float)
    values[0] = innovations[0]
    for index in range(1, n):
        values[index] = phi * values[index - 1] + innovations[index]
    values -= values.mean()
    return values


def _generate_additive(
    rng: np.random.Generator,
    anchor: float,
    day_of_year: np.ndarray,
    spec: dict[str, object],
) -> np.ndarray:
    shape = _seasonal_shape(str(spec["season"]), day_of_year)
    noise = _ar1_noise(
        rng,
        len(day_of_year),
        float(spec["phi"]),
        float(spec["noise_sigma"]),
    )
    low, high = spec["bounds"]  # type: ignore[misc]
    values = anchor + float(spec["amplitude"]) * shape + noise
    values = np.clip(values, low, high)
    for _ in range(4):
        values = np.clip(values - values.mean() + anchor, low, high)
    return values


def _generate_multiplicative(
    rng: np.random.Generator,
    anchor: float,
    day_of_year: np.ndarray,
    spec: dict[str, object],
) -> np.ndarray:
    shape = _seasonal_shape(str(spec["season"]), day_of_year)
    noise = _ar1_noise(
        rng,
        len(day_of_year),
        float(spec["phi"]),
        float(spec["noise_sigma"]),
    )
    low, high = spec["bounds"]  # type: ignore[misc]
    log_factor = float(spec["amplitude"]) * shape + noise
    factor = np.exp(log_factor)
    factor /= factor.mean()
    values = anchor * factor
    values = np.clip(values, low, high)
    for _ in range(4):
        mean_value = float(values.mean())
        if mean_value <= 0:
            break
        values = np.clip(values * (anchor / mean_value), low, high)
    return values


def _load_inputs() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    required = {
        "registry": PROCESSED / "station_registry.csv",
        "annual": PROCESSED / "water_quality_lake_annual.csv",
        "rainfall": PROCESSED / "rainfall_monthly.csv",
        "wind": PROCESSED / "wind_monthly.csv",
    }
    missing = [str(path) for path in required.values() if not path.exists()]
    if missing:
        raise FileNotFoundError(
            "Build the real processed inputs first. Missing: " + ", ".join(missing)
        )

    registry = pd.read_csv(required["registry"])
    annual = pd.read_csv(required["annual"])
    rainfall = pd.read_csv(required["rainfall"])
    wind = pd.read_csv(required["wind"])
    return registry, annual, rainfall, wind


def _lake_stations(registry: pd.DataFrame) -> pd.DataFrame:
    lake = registry.loc[registry["station_type"].eq("lake")].copy()
    lake = lake.reset_index(drop=True)
    if len(lake) != 15:
        raise ValueError(f"Expected 15 lake stations, found {len(lake)}")
    lake["station_id"] = [f"LAG-LAKE-{index:02d}" for index in range(1, len(lake) + 1)]
    lake["reported_lake_zone"] = lake["reported_lake_zone"].fillna("")
    lake["zone_evidence"] = lake["zone_evidence"].fillna("")
    return lake


def _build_anchors(
    lake: pd.DataFrame, annual: pd.DataFrame
) -> pd.DataFrame:
    annual_lake = annual.loc[annual["station_type"].eq("lake")].copy()
    if len(annual_lake) != 150:
        raise ValueError(f"Expected 150 lake station-years, found {len(annual_lake)}")

    records: list[dict[str, object]] = []
    for station in lake.itertuples(index=False):
        station_rows = annual_lake.loc[
            annual_lake["station_name"].eq(station.station_name)
        ]
        if station_rows.empty:
            raise ValueError(f"No annual rows for {station.station_name}")
        if set(station_rows["year"].astype(int)) != set(YEARS):
            raise ValueError(f"Annual years do not match 2016-2025 for {station.station_name}")

        for year in YEARS:
            source_row = station_rows.loc[station_rows["year"].eq(year)].iloc[0]
            for spec in VARIABLE_SPECS:
                raw_value = source_row[spec["annual_column"]]
                source_flag = source_row[spec["flag_column"]]
                source_flag_text = "" if pd.isna(source_flag) else str(source_flag)

                if pd.notna(raw_value):
                    anchor_value = float(raw_value)
                    if year == 2025:
                        anchor_status = "real_annual_summary_2025_completeness_unverified"
                    elif source_flag_text == "ok":
                        anchor_status = "real_annual_summary"
                    else:
                        anchor_status = f"real_annual_summary_source_flag_{source_flag_text}"
                    source_present = "yes"
                else:
                    station_values = station_rows[spec["annual_column"]].dropna()
                    if len(station_values) > 0:
                        anchor_value = float(station_values.mean())
                        anchor_status = "synthetic_station_mean_imputed"
                    else:
                        network_values = annual_lake[spec["annual_column"]].dropna()
                        anchor_value = float(network_values.mean())
                        anchor_status = "synthetic_network_mean_imputed"
                    source_present = "no"

                records.append(
                    {
                        "station_id": station.station_id,
                        "station_name": station.station_name,
                        "year": year,
                        "variable": spec["label"],
                        "variable_key": spec["key"],
                        "anchor_value": round(anchor_value, 6),
                        "unit": spec["unit"],
                        "anchor_status": anchor_status,
                        "source_flag": source_flag_text,
                        "source_numeric_value_present": source_present,
                        "data_origin": "real_annual_anchor_or_synthetic_imputation",
                    }
                )

    anchors = pd.DataFrame.from_records(records)
    if len(anchors) != 15 * 10 * len(VARIABLE_SPECS):
        raise AssertionError("Unexpected anchor row count")
    return anchors


def _build_daily_water_quality(
    lake: pd.DataFrame, anchors: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame]:
    anchor_lookup = {
        (str(row.station_id), int(row.year), str(row.variable_key)): float(row.anchor_value)
        for row in anchors.itertuples(index=False)
    }
    rng = np.random.default_rng(DEFAULT_SEED)
    frames: list[pd.DataFrame] = []
    calibration_records: list[dict[str, object]] = []

    for station in lake.itertuples(index=False):
        for year in YEARS:
            dates = pd.date_range(f"{year}-01-01", f"{year}-12-31", freq="D")
            day_of_year = dates.day_of_year.to_numpy()
            frame = pd.DataFrame(
                {
                    "station_id": station.station_id,
                    "station_name": station.station_name,
                    "station_type": station.station_type,
                    "reported_lake_zone": station.reported_lake_zone,
                    "date": dates.strftime("%Y-%m-%d"),
                    "year": year,
                    "month": dates.month.to_numpy(),
                    "day_of_year": day_of_year,
                }
            )

            for spec in VARIABLE_SPECS:
                anchor = anchor_lookup[(station.station_id, year, spec["key"])]
                if spec["kind"] == "additive":
                    values = _generate_additive(rng, anchor, day_of_year, spec)
                else:
                    values = _generate_multiplicative(rng, anchor, day_of_year, spec)
                values = np.round(values, int(spec["decimals"]))
                frame[spec["daily_column"]] = values

                realized_mean = float(np.mean(values))
                absolute_error = abs(realized_mean - anchor)
                calibration_records.append(
                    {
                        "station_id": station.station_id,
                        "station_name": station.station_name,
                        "year": year,
                        "variable": spec["label"],
                        "variable_key": spec["key"],
                        "unit": spec["unit"],
                        "anchor_value": round(anchor, 6),
                        "realized_daily_mean": round(realized_mean, 6),
                        "absolute_error": round(absolute_error, 6),
                        "relative_error": round(
                            absolute_error / anchor if anchor else 0.0, 8
                        ),
                        "n_days": len(dates),
                        "anchor_status": anchors.loc[
                            (anchors["station_id"].eq(station.station_id))
                            & (anchors["year"].eq(year))
                            & (anchors["variable_key"].eq(spec["key"])),
                            "anchor_status",
                        ].iloc[0],
                        "data_origin": "synthetic_base_v1_calibrated_to_real_annual_anchor",
                    }
                )

            frame["quality_flag"] = "synthetic_ok"
            frame["data_origin"] = DATA_ORIGIN
            frames.append(frame)

    daily = pd.concat(frames, ignore_index=True)
    daily = daily.sort_values(["station_id", "date"], kind="stable").reset_index(drop=True)
    if daily.isna().any().any():
        raise AssertionError("Synthetic daily water-quality table contains missing values")
    return daily, pd.DataFrame.from_records(calibration_records)


def _full_month_grid(years: list[int]) -> pd.DataFrame:
    records = []
    for year in years:
        for month in range(1, 13):
            records.append({"year": year, "month_number": month})
    return pd.DataFrame.from_records(records)


def _monthly_calibration(
    source: pd.DataFrame,
    station_name: str,
    kind: str,
) -> pd.DataFrame:
    station_rows = source.loc[source["station_name"].eq(station_name)].copy()
    if station_rows.empty:
        raise ValueError(f"No monthly {kind} data for {station_name}")

    station_rows = station_rows[["year", "month_number", "value", "quality_flag", "provisional_2025"]]
    station_rows = station_rows.rename(
        columns={
            "value": f"{kind}_raw_value",
            "quality_flag": f"{kind}_raw_quality_flag",
            "provisional_2025": f"{kind}_raw_provisional_2025",
        }
    )
    grid = _full_month_grid(YEARS).merge(
        station_rows,
        on=["year", "month_number"],
        how="left",
    )

    # Month-of-year climatology from the same real station; 2025 partial months
    # are still used only when they contain a numeric value.
    climatology = (
        source.loc[source["station_name"].eq(station_name)]
        .groupby("month_number", dropna=True)["value"]
        .mean()
        .to_dict()
    )
    network_climatology = source.groupby("month_number", dropna=True)["value"].mean().to_dict()

    values: list[float] = []
    statuses: list[str] = []
    provisional: list[str] = []
    raw_value_column = f"{kind}_raw_value"
    raw_provisional_column = f"{kind}_raw_provisional_2025"
    for row in grid.itertuples(index=False):
        raw = getattr(row, raw_value_column)
        if pd.notna(raw):
            values.append(float(raw))
            statuses.append("real_monthly_station_summary")
            raw_provisional = getattr(row, raw_provisional_column)
            provisional.append(
                "" if pd.isna(raw_provisional) else str(raw_provisional)
            )
        else:
            clim = climatology.get(int(row.month_number), np.nan)
            if pd.notna(clim):
                values.append(float(clim))
                statuses.append("synthetic_monthly_station_climatology")
            else:
                net = network_climatology.get(int(row.month_number), np.nan)
                if pd.isna(net):
                    raise ValueError(f"No monthly climatology for {kind}, month {row.month_number}")
                values.append(float(net))
                statuses.append("synthetic_network_monthly_climatology")
            provisional.append("synthetic_fill" if int(row.year) == 2025 else "no")

    grid[f"{kind}_target"] = values
    grid[f"{kind}_calibration_status"] = statuses
    grid[f"{kind}_provisional_2025"] = provisional
    return grid


def _simulate_rainfall(
    rng: np.random.Generator, n_days: int, target_monthly_mm: float
) -> np.ndarray:
    if target_monthly_mm <= 0:
        return np.zeros(n_days, dtype=float)
    wet_probability = min(0.75, 0.10 + 0.55 * min(1.0, target_monthly_mm / 300.0))
    wet_days = rng.random(n_days) < wet_probability
    if not wet_days.any():
        wet_days[rng.integers(0, n_days)] = True
    weights = np.zeros(n_days, dtype=float)
    weights[wet_days] = rng.gamma(shape=1.4, scale=1.0, size=int(wet_days.sum()))
    if weights.sum() <= 0:
        weights[wet_days] = 1.0
    weights /= weights.sum()
    values = np.round(target_monthly_mm * weights, 2)
    return np.maximum(values, 0.0)


def _simulate_wind(
    rng: np.random.Generator, n_days: int, target_monthly_mps: float
) -> np.ndarray:
    noise = _ar1_noise(rng, n_days, 0.65, 0.30)
    values = np.clip(target_monthly_mps + noise, 0.1, None)
    for _ in range(3):
        values = np.clip(values - values.mean() + target_monthly_mps, 0.1, None)
    return np.round(values, 1)


def _simulate_air_temperature(
    rng: np.random.Generator,
    dates: pd.DatetimeIndex,
    offset_c: float,
) -> np.ndarray:
    day_of_year = dates.day_of_year.to_numpy().astype(float)
    seasonal = np.sin(2.0 * np.pi * (day_of_year - 60.0) / 365.25)
    noise = _ar1_noise(rng, len(dates), 0.70, 0.30)
    values = 27.4 + 1.4 * seasonal + offset_c + noise
    return np.round(values, 1)


def _build_daily_weather(
    rainfall: pd.DataFrame, wind: pd.DataFrame
) -> pd.DataFrame:
    rng = np.random.default_rng(DEFAULT_SEED + 1)
    frames: list[pd.DataFrame] = []

    for zone in WEATHER_ZONES:
        rain_grid = _monthly_calibration(
            rainfall, str(zone["calibration_source_station"]), "rainfall"
        )
        wind_grid = _monthly_calibration(
            wind, str(zone["calibration_source_station"]), "wind"
        )
        monthly = rain_grid.merge(wind_grid, on=["year", "month_number"], how="inner")

        zone_frames: list[pd.DataFrame] = []
        for row in monthly.itertuples(index=False):
            year = int(row.year)
            month = int(row.month_number)
            dates = pd.date_range(
                f"{year}-{month:02d}-01",
                periods=int(pd.Period(f"{year}-{month:02d}").days_in_month),
                freq="D",
            )
            frame = pd.DataFrame(
                {
                    "weather_zone_id": zone["weather_zone_id"],
                    "calibration_source_station": zone["calibration_source_station"],
                    "date": dates.strftime("%Y-%m-%d"),
                    "year": year,
                    "month": month,
                    "rainfall_mm": _simulate_rainfall(
                        rng, len(dates), float(row.rainfall_target)
                    ),
                    "wind_mps": _simulate_wind(
                        rng, len(dates), float(row.wind_target)
                    ),
                    "air_temp_c": _simulate_air_temperature(
                        rng, dates, float(zone["air_temp_offset_c"])
                    ),
                    "rainfall_calibration_status": row.rainfall_calibration_status,
                    "wind_calibration_status": row.wind_calibration_status,
                    "provisional_2025": row.rainfall_provisional_2025,
                    "data_origin": DATA_ORIGIN,
                }
            )
            zone_frames.append(frame)

        zone_daily = pd.concat(zone_frames, ignore_index=True)
        if zone_daily.isna().any().any():
            raise AssertionError(f"Synthetic weather table contains missing values for {zone['weather_zone_id']}")
        frames.append(zone_daily)

    weather = pd.concat(frames, ignore_index=True)
    weather = weather.sort_values(["weather_zone_id", "date"], kind="stable").reset_index(drop=True)
    return weather


def _stations_table(lake: pd.DataFrame) -> pd.DataFrame:
    stations = lake[
        [
            "station_id",
            "station_name",
            "station_type",
            "reported_lake_zone",
            "first_source_year",
            "last_source_year",
            "zone_evidence",
        ]
    ].copy()
    stations["coordinates_available"] = "no"
    stations["station_name_is_real"] = "yes"
    stations["values_synthetic"] = "yes"
    stations["data_origin"] = "project_source_station_metadata"
    return stations


def _coverage_table(daily: pd.DataFrame) -> pd.DataFrame:
    value_columns = [spec["daily_column"] for spec in VARIABLE_SPECS]
    records = []
    for year, group in daily.groupby("year", sort=True):
        for spec in VARIABLE_SPECS:
            values = group[spec["daily_column"]]
            records.append(
                {
                    "year": int(year),
                    "variable": spec["label"],
                    "variable_key": spec["key"],
                    "unit": spec["unit"],
                    "rows": int(values.size),
                    "stations": int(group["station_id"].nunique()),
                    "synthetic_min": round(float(values.min()), 4),
                    "synthetic_mean": round(float(values.mean()), 4),
                    "synthetic_max": round(float(values.max()), 4),
                }
            )
    return pd.DataFrame.from_records(records)


def _write_data_dictionary(
    path: Path,
    stations: pd.DataFrame,
    anchors: pd.DataFrame,
    daily: pd.DataFrame,
    weather: pd.DataFrame,
) -> None:
    table_lines = [
        "| File | Rows | Description |",
        "|---|---:|---|",
        f"| `stations.csv` | {len(stations)} | Real lake station labels and supplied zone metadata. No coordinates or measurements are added. |",
        f"| `calibration_anchors.csv` | {len(anchors)} | Real annual station-year anchors where available; synthetic station/network imputations are flagged. |",
        f"| `water_quality_daily.csv` | {len(daily)} | Synthetic daily water-quality values for 15 lake stations, 2016-2025. |",
        f"| `weather_daily.csv` | {len(weather)} | Synthetic daily weather for three synthetic weather zones. |",
        f"| `himpil_synthetic_base.sqlite` | - | SQLite database containing the tables above plus a long-format view and metadata. |",
    ]
    daily_columns = [
        "| Column | Unit / values | Description |",
        "|---|---|---|",
        "| `station_id` | stable synthetic key | `LAG-LAKE-01` to `LAG-LAKE-15`; maps to the real station label. |",
        "| `station_name` | text | Exact lake station label from the supplied LLDA workbooks. |",
        "| `station_type` | `lake` | All rows are lake stations. |",
        "| `reported_lake_zone` | text or blank | Zone only where the real station label states one. Blank means not supplied. |",
        "| `date` | `YYYY-MM-DD` | Synthetic daily calendar date. |",
        "| `nitrate_mg_l` | mg/L | Synthetic daily nitrate. |",
        "| `phosphate_mg_l` | mg/L | Synthetic daily phosphate. |",
        "| `bod_mg_l` | mg/L | Synthetic daily biochemical oxygen demand. |",
        "| `ph` | pH units | Synthetic daily pH. |",
        "| `water_temp_c` | deg C | Synthetic daily water temperature. |",
        "| `do_mg_l` | mg/L | Synthetic daily dissolved oxygen. |",
        "| `quality_flag` | `synthetic_ok` | Every daily water-quality row is synthetic. |",
        "| `data_origin` | `synthetic_base_v1` | Quarantine marker. |",
    ]
    anchor_columns = [
        "| Column | Unit / values | Description |",
        "|---|---|---|",
        "| `station_id`, `station_name` | keys | Station mapping used by the daily table. |",
        "| `year` | 2016-2025 | Calendar year of the annual anchor. |",
        "| `variable`, `variable_key` | text | Variable label and stable key. |",
        "| `anchor_value` | variable unit | Real annual value where present; imputed value where missing. |",
        "| `unit` | text | mg/L, pH units, or deg C. |",
        "| `anchor_status` | text | `real_annual_summary`, `real_annual_summary_2025_completeness_unverified`, `synthetic_station_mean_imputed`, or `synthetic_network_mean_imputed`. |",
        "| `source_flag` | text | Original source missing/quality flag. |",
        "| `source_numeric_value_present` | yes/no | Whether a real numeric annual value existed before imputation. |",
    ]
    weather_columns = [
        "| Column | Unit / values | Description |",
        "|---|---|---|",
        "| `weather_zone_id` | synthetic key | `SYN-WX-WEST`, `SYN-WX-CENTRAL`, or `SYN-WX-EAST`. |",
        "| `calibration_source_station` | real PAGASA label | Monthly target source; not a real station-to-lake mapping. |",
        "| `date` | `YYYY-MM-DD` | Synthetic daily date. |",
        "| `rainfall_mm` | mm/day | Synthetic daily rainfall, calibrated to a real nearby monthly summary. |",
        "| `wind_mps` | m/s | Synthetic daily wind speed, calibrated to a real nearby monthly summary. |",
        "| `air_temp_c` | deg C | Synthetic daily air temperature; no real daily air-temperature source was supplied. |",
        "| `rainfall_calibration_status`, `wind_calibration_status` | text | Real monthly summary or synthetic climatology fill. |",
        "| `provisional_2025` | yes/no/synthetic_fill | 2025 source status; `synthetic_fill` means the source had no month value. |",
        "| `data_origin` | `synthetic_base_v1` | Quarantine marker. |",
    ]
    text = f"""# Synthetic base data dictionary

> **{WARNING}**

This folder contains a synthetic daily base dataset. It is **not** evidence about
Laguna de Bay. The station labels, source years, variables, and units come from
the project's real source inventory; the daily values do not.

## Tables

{chr(10).join(table_lines)}

## Daily water-quality columns

{chr(10).join(daily_columns)}

## Calibration-anchor columns

{chr(10).join(anchor_columns)}

## Daily weather columns

{chr(10).join(weather_columns)}

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
"""
    path.write_text(text, encoding="utf-8")


def _write_readme(path: Path) -> None:
    text = f"""# HIMPIL synthetic base dataset

> **{WARNING}**
>
> This is a synthetic base dataset built from the project's real station labels,
> years, variables, units, and annual anchors. The daily values are generated.
> The annual anchors are real source values included only for calibration and
> audit. No daily value is a measurement of Laguna de Bay. Nothing here is a real
> fish-kill record or can support a real risk assessment.

## What this is

A quarantined, reproducible daily base dataset for software and workflow testing:

- 15 lake station labels from the supplied LLDA workbooks;
- 2016-01-01 through 2025-12-31;
- six water-quality variables: nitrate, phosphate, BOD, pH, water temperature, DO;
- three synthetic weather zones with rainfall, wind, and air temperature;
- real annual station-year anchors where available, with missing cells imputed and flagged.

## What this is not

- It is not evidence about Laguna de Bay.
- It is not the real HIMPIL model dataset.
- It does not contain fish-kill labels or real event dates.
- It does not satisfy the Section 6 model-readiness gate.
- It must not be connected to the evidence dashboard.

The real dashboard must continue to report **risk assessment unavailable**.

## Files

| File | Description |
|---|---|
| `stations.csv` | Real station labels and supplied zone metadata; no coordinates. |
| `calibration_anchors.csv` | Annual anchors and imputation flags used by the generator. |
| `water_quality_daily.csv` | Synthetic daily water-quality panel, wide format. |
| `weather_daily.csv` | Synthetic daily weather for three synthetic zones. |
| `himpil_synthetic_base.sqlite` | SQLite database with tables, a long-format view, and metadata. |
| `data_dictionary.md` | Column definitions, units, calibration method, and limits. |
| `manifest.json` | Seed, source hashes, counts, calibration summary, and quarantine flags. |

## Quick query

The SQLite file has a wide table and a long-format view:

```sql
SELECT station_name, date, do_mg_l
  FROM water_quality_daily
 WHERE station_id = 'LAG-LAKE-01'
 ORDER BY date
 LIMIT 10;

SELECT *
  FROM water_quality_daily_long
 LIMIT 10;
```

## Regeneration

```powershell
.\\.venv\\Scripts\\python.exe sandbox\\synthetic\\build_base_dataset.py
```

The generator is deterministic by default (seed `{DEFAULT_SEED}`). It reads the
real processed inputs but writes only to this folder and to the synthetic-base
report files under `reports/tables/`.

## Quarantine rules

1. Do not copy these files into `data/processed/`.
2. Do not replace `models/model.joblib` with a model trained on these data.
3. Do not load these values into `dashboard/src/data/dashboard.json`.
4. Do not describe a synthetic value as a Laguna de Bay measurement.
5. Do not use this dataset to issue an advisory.
6. Do not claim the real model gate passed.

See [`../../../sandbox/synthetic/README.md`](../../../sandbox/synthetic/README.md)
and [`../../../reports/tables/synthetic_base_report.md`](../../../reports/tables/synthetic_base_report.md).
"""
    path.write_text(text, encoding="utf-8")


def _write_report(
    path: Path,
    stations: pd.DataFrame,
    anchors: pd.DataFrame,
    daily: pd.DataFrame,
    weather: pd.DataFrame,
    calibration: pd.DataFrame,
) -> None:
    max_error = calibration["absolute_error"].max()
    mean_error = calibration["absolute_error"].mean()
    real_anchor_count = int(
        anchors["source_numeric_value_present"].eq("yes").sum()
    )
    imputed_count = int(
        anchors["source_numeric_value_present"].eq("no").sum()
    )
    provisional_count = int(
        anchors["anchor_status"].eq(
            "real_annual_summary_2025_completeness_unverified"
        ).sum()
    )
    zone_lines = "\n".join(
        f"| `{zone['weather_zone_id']}` | `{zone['calibration_source_station']}` |"
        for zone in WEATHER_ZONES
    )
    text = f"""# Synthetic base dataset report

> **{WARNING}**

This report describes a synthetic base dataset. It is **not** evidence about
Laguna de Bay and does **not** pass the Section 6 gate. The real dashboard must
continue to show **risk assessment unavailable**.

## Coverage

- Lake stations: **{len(stations)}** (exact labels from the supplied workbooks).
- Calendar: **2016-01-01 to 2025-12-31** (synthetic daily dates).
- Water-quality rows: **{len(daily):,}** station-days.
- Water-quality variables: **{len(VARIABLE_SPECS)}**.
- Weather rows: **{len(weather):,}** across **{weather['weather_zone_id'].nunique()}** synthetic zones.
- Annual anchors: **{len(anchors):,}** station-year-variable rows.
  - Real numeric anchors: **{real_anchor_count:,}**.
  - Synthetic imputed anchors: **{imputed_count:,}**.
  - 2025 anchors with unverified completeness: **{provisional_count:,}**.

## Calibration

The daily series are calibrated to the annual anchors. Realized annual means are
reported in `synthetic_base_calibration.csv`.

- Mean absolute annual-mean error: **{mean_error:.6f}**.
- Maximum absolute annual-mean error: **{max_error:.6f}**.

Exact equality is not guaranteed because values are clipped to plausible
variable bounds and rounded to the displayed precision.

## Stations

| Station ID | Real station label | Supplied zone |
|---|---|---|
{chr(10).join(f"| `{row.station_id}` | {row.station_name} | {row.reported_lake_zone or '(blank)'} |" for row in stations.itertuples(index=False))}

## Weather zones

These are synthetic zones. The calibration station is a real PAGASA summary used
only to shape monthly rainfall and wind; no real station-to-lake mapping is
claimed.

| Synthetic weather zone | Calibration source |
|---|---|
{zone_lines}

## Missingness and imputation

- Ten of the fifteen lake stations have no zone label in the source; their zone
  remains blank.
- The real annual water-temperature cell is missing for **39 station-years**,
  including all 15 in 2017; synthetic values are imputed and flagged.
- 2025 source values exist but their completeness is not documented; they are
  retained with an explicit flag.
- Synthetic daily values are complete by design. This is a convenience for
  software testing, not a claim that real monitoring is complete.

## What is absent

- No fish-kill labels.
- No real or synthetic event dates tied to a real incident.
- No station coordinates.
- No tributary stations; only the 15 lake stations are generated.
- No model training, metrics, risk scores, or advisories.
- No connection to `data/processed/` or the evidence dashboard.

## Files

- `data/synthetic/base/` — CSV, SQLite, data dictionary, manifest, README.
- `reports/tables/synthetic_base_calibration.csv` — annual calibration audit.
- `reports/tables/synthetic_base_coverage.csv` — synthetic ranges by year/variable.
- `reports/tables/synthetic_base_report.md` — this report.
"""
    path.write_text(text, encoding="utf-8")


def _build_sqlite(
    path: Path,
    stations: pd.DataFrame,
    anchors: pd.DataFrame,
    daily: pd.DataFrame,
    weather: pd.DataFrame,
    manifest: dict[str, object],
) -> None:
    if path.exists():
        path.unlink()
    with sqlite3.connect(path) as connection:
        stations.to_sql("stations", connection, index=False, if_exists="replace")
        anchors.to_sql("calibration_anchors", connection, index=False, if_exists="replace")
        daily.to_sql("water_quality_daily", connection, index=False, if_exists="replace")
        weather.to_sql("weather_daily", connection, index=False, if_exists="replace")

        metadata = pd.DataFrame(
            [
                ("dataset", "himpil_synthetic_base"),
                ("version", "1.0"),
                ("status", "synthetic_base_only"),
                ("warning", WARNING),
                ("seed", str(DEFAULT_SEED)),
                ("data_origin", DATA_ORIGIN),
                ("generated_at_utc", str(manifest["generated_at_utc"])),
                ("quarantine", "not evidence; do not load into the evidence dashboard"),
            ],
            columns=["key", "value"],
        )
        metadata.to_sql("metadata", connection, index=False, if_exists="replace")

        connection.executescript(
            """
            CREATE INDEX IF NOT EXISTS idx_wq_station_date
                ON water_quality_daily(station_id, date);
            CREATE INDEX IF NOT EXISTS idx_wq_date
                ON water_quality_daily(date);
            CREATE INDEX IF NOT EXISTS idx_anchors_station_year
                ON calibration_anchors(station_id, year, variable_key);
            CREATE INDEX IF NOT EXISTS idx_weather_zone_date
                ON weather_daily(weather_zone_id, date);

            DROP VIEW IF EXISTS water_quality_daily_long;
            CREATE VIEW water_quality_daily_long AS
            SELECT station_id, station_name, station_type, reported_lake_zone, date, year, month,
                   'Nitrate' AS variable, nitrate_mg_l AS value, 'mg/L' AS unit,
                   quality_flag, data_origin
              FROM water_quality_daily
            UNION ALL
            SELECT station_id, station_name, station_type, reported_lake_zone, date, year, month,
                   'Phosphate' AS variable, phosphate_mg_l AS value, 'mg/L' AS unit,
                   quality_flag, data_origin
              FROM water_quality_daily
            UNION ALL
            SELECT station_id, station_name, station_type, reported_lake_zone, date, year, month,
                   'BOD' AS variable, bod_mg_l AS value, 'mg/L' AS unit,
                   quality_flag, data_origin
              FROM water_quality_daily
            UNION ALL
            SELECT station_id, station_name, station_type, reported_lake_zone, date, year, month,
                   'pH' AS variable, ph AS value, 'pH units' AS unit,
                   quality_flag, data_origin
              FROM water_quality_daily
            UNION ALL
            SELECT station_id, station_name, station_type, reported_lake_zone, date, year, month,
                   'Water temperature' AS variable, water_temp_c AS value, 'deg C' AS unit,
                   quality_flag, data_origin
              FROM water_quality_daily
            UNION ALL
            SELECT station_id, station_name, station_type, reported_lake_zone, date, year, month,
                   'Dissolved oxygen (DO)' AS variable, do_mg_l AS value, 'mg/L' AS unit,
                   quality_flag, data_origin
              FROM water_quality_daily;
            """
        )


def main() -> None:
    global DEFAULT_SEED

    parser = argparse.ArgumentParser(description="Build the quarantined HIMPIL synthetic base dataset.")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    DEFAULT_SEED = int(args.seed)
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    TABLES.mkdir(parents=True, exist_ok=True)

    registry, annual, rainfall, wind = _load_inputs()
    lake = _lake_stations(registry)
    stations = _stations_table(lake)
    anchors = _build_anchors(lake, annual)
    daily, calibration = _build_daily_water_quality(lake, anchors)
    weather = _build_daily_weather(rainfall, wind)
    coverage = _coverage_table(daily)

    stations_path = output_dir / "stations.csv"
    anchors_path = output_dir / "calibration_anchors.csv"
    daily_path = output_dir / "water_quality_daily.csv"
    weather_path = output_dir / "weather_daily.csv"
    sqlite_path = output_dir / "himpil_synthetic_base.sqlite"
    dictionary_path = output_dir / "data_dictionary.md"
    manifest_path = output_dir / "manifest.json"
    readme_path = output_dir / "README.md"

    stations.to_csv(stations_path, index=False, encoding="utf-8-sig")
    anchors.to_csv(anchors_path, index=False, encoding="utf-8-sig")
    daily.to_csv(daily_path, index=False, encoding="utf-8-sig")
    weather.to_csv(weather_path, index=False, encoding="utf-8-sig")

    calibration_path = TABLES / "synthetic_base_calibration.csv"
    coverage_path = TABLES / "synthetic_base_coverage.csv"
    report_path = TABLES / "synthetic_base_report.md"
    calibration.to_csv(calibration_path, index=False, encoding="utf-8-sig")
    coverage.to_csv(coverage_path, index=False, encoding="utf-8-sig")

    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    manifest: dict[str, object] = {
        "dataset": "himpil_synthetic_base",
        "version": "1.0",
        "status": "synthetic_base_only",
        "warning": WARNING,
        "data_origin": DATA_ORIGIN,
        "generated_at_utc": generated_at,
        "seed": DEFAULT_SEED,
        "source_files": {
            "station_registry": _relative(PROCESSED / "station_registry.csv"),
            "water_quality_lake_annual": _relative(PROCESSED / "water_quality_lake_annual.csv"),
            "rainfall_monthly": _relative(PROCESSED / "rainfall_monthly.csv"),
            "wind_monthly": _relative(PROCESSED / "wind_monthly.csv"),
        },
        "source_hashes_sha256": {
            _relative(PROCESSED / "station_registry.csv"): _sha256(PROCESSED / "station_registry.csv"),
            _relative(PROCESSED / "water_quality_lake_annual.csv"): _sha256(PROCESSED / "water_quality_lake_annual.csv"),
            _relative(PROCESSED / "rainfall_monthly.csv"): _sha256(PROCESSED / "rainfall_monthly.csv"),
            _relative(PROCESSED / "wind_monthly.csv"): _sha256(PROCESSED / "wind_monthly.csv"),
        },
        "coverage": {
            "stations": int(len(stations)),
            "start_date": str(daily["date"].min()),
            "end_date": str(daily["date"].max()),
            "water_quality_rows": int(len(daily)),
            "weather_rows": int(len(weather)),
            "weather_zones": int(weather["weather_zone_id"].nunique()),
            "variables": [spec["label"] for spec in VARIABLE_SPECS],
        },
        "anchors": {
            "rows": int(len(anchors)),
            "real_numeric_values": int(anchors["source_numeric_value_present"].eq("yes").sum()),
            "synthetic_imputations": int(anchors["source_numeric_value_present"].eq("no").sum()),
            "2025_unverified_completeness": int(
                anchors["anchor_status"].eq(
                    "real_annual_summary_2025_completeness_unverified"
                ).sum()
            ),
        },
        "calibration": {
            "mean_absolute_annual_mean_error": round(float(calibration["absolute_error"].mean()), 8),
            "max_absolute_annual_mean_error": round(float(calibration["absolute_error"].max()), 8),
        },
        "weather_zones": WEATHER_ZONES,
        "quarantine": {
            "not_evidence": True,
            "does_not_satisfy_model_gate": True,
            "not_connected_to_dashboard": True,
            "contains_fish_kill_labels": False,
            "contains_real_station_labels": True,
            "contains_real_annual_anchors": True,
            "contains_real_daily_measurements": False,
            "contains_station_coordinates": False,
        },
        "limitations": [
            "Daily values are synthetic and are calibrated only to annual station means.",
            "Seasonal shapes, noise, and weather-zone mapping are simulation choices.",
            "Ten of fifteen lake stations have no supplied zone label.",
            "2025 annual anchors have unverified source completeness.",
            "Tributary stations in the real registry are not generated.",
            "No fish-kill labels, real event dates, coordinates, or risk scores are included.",
        ],
    }

    _write_data_dictionary(dictionary_path, stations, anchors, daily, weather)
    _write_readme(readme_path)
    _write_report(report_path, stations, anchors, daily, weather, calibration)
    _build_sqlite(sqlite_path, stations, anchors, daily, weather, manifest)

    output_paths = [
        stations_path,
        anchors_path,
        daily_path,
        weather_path,
        sqlite_path,
        dictionary_path,
        readme_path,
    ]
    manifest["output_hashes_sha256"] = {
        _relative(path): _sha256(path) for path in output_paths
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"{WARNING}")
    print(f"Wrote synthetic base dataset to {output_dir}")
    print(f"  stations: {len(stations)}")
    print(f"  daily water-quality rows: {len(daily):,}")
    print(f"  weather rows: {len(weather):,}")
    print(f"  annual anchors: {len(anchors):,}")
    print(
        "  calibration max abs error: "
        f"{float(calibration['absolute_error'].max()):.6f}"
    )
    print(f"  SQLite: {sqlite_path.name}")
    print(f"  report: {_relative(report_path)}")


if __name__ == "__main__":
    main()
