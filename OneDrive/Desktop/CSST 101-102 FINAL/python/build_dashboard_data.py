"""Build the static data bundle for the HIMPIL dashboard.

The dashboard is a presentation layer. It reads only documented CSV outputs;
it never reaches into the original workbooks and never invents observations.

Outputs:
    dashboard/src/data/dashboard.json
    dashboard/public/figures/*.png (selected R figures, copied)
"""

from __future__ import annotations

import json
import math
import shutil
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from common import (
    FIGURE_DIR,
    OUTPUT_DIR,
    PROCESSED_DIR,
    PROJECT_ROOT,
    TABLE_DIR,
    VARIABLES,
    read_csv,
)
from real_trend import fit_annual_trends

DASHBOARD_DIR = PROJECT_ROOT / "dashboard"
DATA_DIR = DASHBOARD_DIR / "src" / "data"
PUBLIC_FIGURE_DIR = DASHBOARD_DIR / "public" / "figures"
REQUESTS_DIR = PROJECT_ROOT / "reports" / "data_requests"


def scalar(value):
    if value is None:
        return None
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        value = float(value)
    if isinstance(value, float):
        return None if math.isnan(value) or math.isinf(value) else round(value, 6)
    if pd.isna(value):
        return None
    return value


def records(frame: pd.DataFrame) -> list[dict]:
    return [
        {key: scalar(value) for key, value in row.items()}
        for row in frame.to_dict(orient="records")
    ]


def sanitize(value):
    """Recursively remove pandas/NumPy NaN values before JSON serialisation."""
    if isinstance(value, dict):
        return {str(key): sanitize(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [sanitize(item) for item in value]
    return scalar(value)


def network_years(frame: pd.DataFrame, value_column: str) -> list[dict]:
    rows = []
    for row in frame.to_dict(orient="records"):
        rows.append({
            "year": int(row["year"]),
            "n": int(row["n_stations"]),
            "mean": scalar(row[value_column]),
            "min": scalar(row.get("minimum")),
            "max": scalar(row.get("maximum")),
        })
    return rows


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    PUBLIC_FIGURE_DIR.mkdir(parents=True, exist_ok=True)

    lake = pd.read_csv(PROCESSED_DIR / "water_quality_lake_annual.csv")
    real_alignment = fit_annual_trends(lake)
    wq_long = pd.read_csv(PROCESSED_DIR / "water_quality_long.csv")
    rainfall = pd.read_csv(PROCESSED_DIR / "rainfall_monthly.csv")
    wind = pd.read_csv(PROCESSED_DIR / "wind_monthly.csv")
    station_registry = pd.read_csv(PROCESSED_DIR / "station_registry.csv")
    events = pd.read_csv(PROCESSED_DIR / "historical_fish_kill_events.csv")
    audit = pd.read_csv(PROCESSED_DIR / "incident_evidence_audit.csv")
    sources = pd.read_csv(TABLE_DIR / "source_inventory.csv")
    requests_log = pd.read_csv(REQUESTS_DIR / "data_access_log.csv")
    readiness = pd.read_csv(PROCESSED_DIR / "labeling_readiness.csv")
    labeling = pd.read_csv(PROCESSED_DIR / "labeling_summary.csv")
    training = pd.read_csv(OUTPUT_DIR / "training_status.csv")
    evaluation = pd.read_csv(OUTPUT_DIR / "evaluation_status.csv")

    lake_numeric = wq_long[
        (wq_long["station_type"] == "lake")
        & (wq_long["quality_flag"].isin(["ok", "out_of_range"]))
        & wq_long["value"].notna()
    ].copy()

    variable_order = [spec["name"] for spec in VARIABLES.values()]
    water_variables = []
    for variable in variable_order:
        unit = VARIABLES[[key for key, spec in VARIABLES.items() if spec["name"] == variable][0]]["unit"]
        data = lake_numeric[lake_numeric["variable"] == variable]
        if data.empty:
            continue
        grouped = (
            data.groupby("year")
            .agg(
                n_stations=("value", "size"),
                mean=("value", "mean"),
                minimum=("value", "min"),
                maximum=("value", "max"),
            )
            .reset_index()
        )
        years = network_years(grouped, "mean")
        latest = next((point for point in reversed(years) if point["mean"] is not None), None)
        summary = {
            "n": int(len(data)),
            "mean": scalar(data["value"].mean()),
            "median": scalar(data["value"].median()),
            "min": scalar(data["value"].min()),
            "max": scalar(data["value"].max()),
        }
        water_variables.append({
            "key": variable,
            "label": variable.replace(" (DO)", ""),
            "unit": unit,
            "years": years,
            "latest": latest,
            "summary": summary,
        })

    # Per-station-year measurements for the monitoring table.
    measurements = []
    for row in lake_numeric.sort_values(["year", "station_name", "variable"]).to_dict(orient="records"):
        measurements.append({
            "station": row["station_name"],
            "zone": scalar(row.get("reported_lake_zone")) or "",
            "year": int(row["year"]),
            "variable": row["variable"],
            "value": scalar(row["value"]),
            "unit": row["unit"],
            "quality": row["quality_flag"],
        })

    lake_stations = station_registry[station_registry["station_type"] == "lake"].copy()
    stations = []
    for row in lake_stations.to_dict(orient="records"):
        stations.append({
            "name": row["station_name"],
            "zone": scalar(row.get("reported_lake_zone")) or "",
            "firstYear": scalar(row.get("first_numeric_year")),
            "lastYear": scalar(row.get("last_numeric_year")),
            "numericYears": scalar(row.get("numeric_years_count")),
            "variables": scalar(row.get("variables_present_in_source")),
            "zoneEvidence": row.get("zone_evidence"),
        })

    # Weather annual totals/means from complete 12-month station-years.
    def weather_annual(frame: pd.DataFrame, value_column: str, aggregate: str) -> pd.DataFrame:
        clean = frame[
            frame["quality_flag"].isin(["ok", "out_of_range"])
            & frame["value"].notna()
            & (frame["year"] <= 2024)
        ]
        station_year = (
            clean.groupby(["station_name", "year"])
            .agg(n_months=("value", "size"), total=("value", "sum"), mean=("value", "mean"))
            .reset_index()
        )
        station_year = station_year[station_year["n_months"] == 12]
        value = "total" if aggregate == "sum" else "mean"
        return (
            station_year.groupby("year")
            .agg(
                n_stations=(value, "size"),
                mean=(value, "mean"),
                minimum=(value, "min"),
                maximum=(value, "max"),
            )
            .reset_index()
        )

    rain_years_frame = weather_annual(rainfall, "value", "sum")
    wind_years_frame = weather_annual(wind, "value", "mean")
    rain_years = [
        {
            "year": int(row["year"]),
            "n": int(row["n_stations"]),
            "mean": scalar(row["mean"]),
            "min": scalar(row["minimum"]),
            "max": scalar(row["maximum"]),
        }
        for row in rain_years_frame.to_dict(orient="records")
    ]
    wind_years = [
        {
            "year": int(row["year"]),
            "n": int(row["n_stations"]),
            "mean": scalar(row["mean"]),
            "min": scalar(row["minimum"]),
            "max": scalar(row["maximum"]),
        }
        for row in wind_years_frame.to_dict(orient="records")
    ]

    # A single lake-area rainfall view. Tanay, Rizal is the only station in the
    # supplied PAGASA list that is clearly in the Laguna de Bay watershed. This
    # is descriptive context, not a lake measurement and not a model input.
    tanay_station = "Tanay, Rizal"
    tanay = rainfall[rainfall["station_name"].eq(tanay_station)].copy()
    if tanay.empty:
        raise ValueError(f"Required rainfall station not found: {tanay_station}")
    tanay_complete = tanay[
        tanay["year"].le(2024)
        & tanay["value"].notna()
        & tanay["quality_flag"].isin(["ok", "out_of_range"])
    ].copy()
    tanay_station_year = (
        tanay_complete.groupby("year", as_index=False)
        .agg(months=("value", "size"), total=("value", "sum"))
        .sort_values("year")
    )
    tanay_station_year = tanay_station_year[tanay_station_year["months"] == 12]
    tanay_years = [
        {
            "year": int(row["year"]),
            "total": scalar(row["total"]),
            "months": int(row["months"]),
        }
        for row in tanay_station_year.to_dict(orient="records")
    ]
    tanay_latest = tanay_years[-1] if tanay_years else None
    tanay_complete_years = set(tanay_station_year["year"].tolist())
    tanay_monthly_frame = (
        tanay_complete[tanay_complete["year"].isin(tanay_complete_years)]
        .groupby(["month_number", "month"], as_index=False)
        .agg(
            mean=("value", "mean"),
            minimum=("value", "min"),
            maximum=("value", "max"),
            years=("year", "nunique"),
        )
        .sort_values("month_number")
    )
    tanay_monthly = [
        {
            "month": int(row["month_number"]),
            "label": row["month"],
            "mean": scalar(row["mean"]),
            "min": scalar(row["minimum"]),
            "max": scalar(row["maximum"]),
            "years": int(row["years"]),
        }
        for row in tanay_monthly_frame.to_dict(orient="records")
    ]
    tanay_2025 = tanay[
        tanay["year"].eq(2025)
        & tanay["value"].notna()
        & tanay["quality_flag"].isin(["ok", "out_of_range"])
    ]
    tanay_partial = {
        "year": 2025,
        "total": scalar(tanay_2025["value"].sum()) if len(tanay_2025) else None,
        "months": int(len(tanay_2025)),
        "note": "January–June only; not an annual total.",
    }
    tanay_source_ids = sorted(
        str(value) for value in tanay["source_id"].dropna().unique()
    )

    latest_do = next(
        (variable for variable in water_variables if variable["key"] == "Dissolved oxygen (DO)"),
        None,
    )
    latest_temp = next(
        (variable for variable in water_variables if variable["key"] == "Water temperature"),
        None,
    )
    latest_rain = next((point for point in reversed(rain_years) if point["mean"] is not None), None)
    latest_wind = next((point for point in reversed(wind_years) if point["mean"] is not None), None)

    metrics = [
        {
            "id": "do",
            "label": "Dissolved oxygen",
            "value": latest_do["latest"]["mean"] if latest_do else None,
            "display": f"{latest_do['latest']['mean']:.2f}" if latest_do else "—",
            "unit": "mg/L",
            "period": "2025 network mean of annual summaries",
            "detail": f"{latest_do['latest']['n']} lake stations; per-station source aggregation undocumented",
            "note": "Not a daily measurement",
            "points": [point["mean"] for point in latest_do["years"]] if latest_do else [],
        },
        {
            "id": "temperature",
            "label": "Water temperature",
            "value": latest_temp["latest"]["mean"] if latest_temp else None,
            "display": f"{latest_temp['latest']['mean']:.2f}" if latest_temp else "—",
            "unit": "°C",
            "period": "2025 network mean of annual summaries",
            "detail": f"{latest_temp['latest']['n']} lake stations; per-station source aggregation undocumented",
            "note": "Not a daily measurement",
            "points": [point["mean"] for point in latest_temp["years"]] if latest_temp else [],
        },
        {
            "id": "rain",
            "label": "Rainfall",
            "value": latest_rain["mean"] if latest_rain else None,
            "display": f"{latest_rain['mean']:,.0f}" if latest_rain else "—",
            "unit": "mm/year",
            "period": f"{latest_rain['year']} network mean" if latest_rain else "No complete year",
            "detail": f"{latest_rain['n']} stations with 12 numeric months",
            "note": "2025 excluded; incomplete and still undergoing verification",
            "points": [point["mean"] for point in rain_years],
        },
        {
            "id": "wind",
            "label": "Wind speed",
            "value": latest_wind["mean"] if latest_wind else None,
            "display": f"{latest_wind['mean']:.2f}" if latest_wind else "—",
            "unit": "m/s",
            "period": f"{latest_wind['year']} network mean" if latest_wind else "No complete year",
            "detail": f"{latest_wind['n']} stations with 12 numeric months",
            "note": "2025 excluded; incomplete and still undergoing verification",
            "points": [point["mean"] for point in wind_years],
        },
    ]

    coverage = {
        "lakeStations": int(lake["station_name"].nunique()),
        "lakeStationYears": int(len(lake)),
        "completeStationYears": int((lake["all_six_reported"] == "yes").sum()),
        "numericWaterQualityValues": int(len(lake_numeric)),
        "datedWaterQualityRows": 0,
        "rainNumericMonths": int(rainfall["value"].notna().sum()),
        "windNumericMonths": int(wind["value"].notna().sum()),
        "sourceCount": int(len(sources)),
        "eventReports": int(len(events)),
        "verifiedEvents": 0,
        "lakeStationsWithZoneLabel": int((lake_stations["reported_lake_zone"].fillna("") != "").sum()),
    }

    feasibility = {row["metric"]: scalar(row["value"]) for row in labeling.to_dict(orient="records")}
    readiness_rows = [
        {
            "check": row["check_id"],
            "requirement": row["requirement"],
            "status": row["status"],
            "evidence": row["evidence"],
            "consequence": row["consequence"],
        }
        for row in readiness.to_dict(orient="records")
    ]
    training_rows = [
        {
            "check": row["check"],
            "requirement": row["requirement"],
            "status": row["status"],
            "evidence": row["evidence"],
        }
        for row in training.to_dict(orient="records")
    ]
    evaluation_rows = [
        {
            "check": row["check"],
            "requirement": row["requirement"],
            "status": row["status"],
            "evidence": row["evidence"],
        }
        for row in evaluation.to_dict(orient="records")
    ]

    event_rows = []
    for row in events.to_dict(orient="records"):
        event_rows.append({
            "id": row["event_id"],
            "start": row["event_start_date"],
            "end": row["event_end_date"],
            "location": row["location"],
            "municipality": row["municipality"],
            "zone": scalar(row.get("lake_zone")) or "",
            "species": row["fish_species"],
            "losses": row["estimated_fish_losses"],
            "economicLoss": scalar(row.get("estimated_economic_loss")) or "",
            "cause": row["reported_cause"],
            "sourceTitle": row["source_title"],
            "sourceUrl": row["source_url"],
            "publicationDate": row["publication_date"],
            "datePrecision": row["date_precision"],
            "locationPrecision": row["location_precision"],
            "verification": row["verification_status"],
            "notes": row["notes"],
        })

    audit_rows = [
        {
            "id": row["candidate_id"],
            "claim": row["claim"],
            "source": row["source_id"],
            "locator": row["source_locator"],
            "issue": row["issue"],
            "decision": row["decision"],
            "reason": row["reason"],
        }
        for row in audit.to_dict(orient="records")
    ]

    source_rows = []
    for row in sources.to_dict(orient="records"):
        source_rows.append({
            "id": scalar(row["source_id"]) or "",
            "filename": scalar(row["filename"]) or "",
            "type": scalar(row["source_type"]) or "",
            "organization": scalar(row["source_organization"]) or "",
            "publication": scalar(row["publication_date"]) or "",
            "period": scalar(row["reporting_period"]) or "",
            "content": scalar(row["content_type"]) or "",
            "incidents": scalar(row["individual_incident_records"]) or "",
            "labels": scalar(row["fish_kill_label_suitability"]) or "",
            "used": scalar(row["used_in_himpil_pipeline"]) or "",
        })

    figure_specs = [
        (
            "fig_water_quality_completeness.png",
            "Station-year completeness",
            "Number of six lake variables reported for each station-year.",
        ),
        (
            "fig_nutrients_by_year.png",
            "Nutrient and BOD distributions",
            "Annual station values, not daily observations.",
        ),
        (
            "fig_rainfall_year_month.png",
            "Rainfall by year and month",
            "Network mean monthly rainfall; 2025 excluded.",
        ),
    ]
    figure_rows = []
    for filename, title, caption in figure_specs:
        source_path = FIGURE_DIR / filename
        if source_path.exists():
            shutil.copy2(source_path, PUBLIC_FIGURE_DIR / filename)
            figure_rows.append({
                "file": f"figures/{filename}",
                "title": title,
                "caption": caption,
            })

    request_summary = {
        "total": int(len(requests_log)),
        "acknowledged": int((requests_log["status"] == "acknowledged").sum()),
        "planned": int((requests_log["status"] == "planned").sum()),
        "received": int((requests_log["status"] == "received").sum()),
        "files": int(
            (
                requests_log["files_received"].notna()
                & (
                    requests_log["files_received"]
                    .astype(str)
                    .str.strip()
                    .replace({"nan": "", "None": ""})
                    != ""
                )
            ).sum()
        ),
        "outreachPaused": True,
        "note": (
            "Outreach paused by team decision (D-009, 2026-10-23). "
            "No data files or permissions received."
        ),
    }

    dashboard = {
        "generatedAtUtc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "project": {
            "name": "HIMPIL",
            "subtitle": "Environmental Intelligence for Laguna de Bay",
            "studyArea": "Laguna de Bay, Philippines",
            "status": "Research prototype — not an official warning service",
            "dataDates": "Water quality: 2016–2025 annual summaries; weather: 2016–2025 monthly summaries",
        },
        "coverage": coverage,
        "metrics": metrics,
        "realAlignment": {
            key: value
            for key, value in real_alignment.items()
            if key != "notes"
        },
        "waterQuality": {
            "variables": water_variables,
            "stations": stations,
            "measurements": measurements,
            "note": "All values are annual station summaries. No observation date, aggregation rule or station coordinate is supplied.",
        },
        "weather": {
            "rainfall": {"years": rain_years, "latest": latest_rain, "unit": "mm/year"},
            "wind": {"years": wind_years, "latest": latest_wind, "unit": "m/s"},
            "lakeArea": {
                "stationName": tanay_station,
                "sourceId": ", ".join(tanay_source_ids),
                "role": (
                    "Only station in the supplied list that is clearly in the "
                    "Laguna de Bay watershed; a regional proxy, not a lake "
                    "station."
                ),
                "years": tanay_years,
                "latest": tanay_latest,
                "partial2025": tanay_partial,
                "monthly": tanay_monthly,
                "note": (
                    "Complete 12-month station-years only, 2016–2024. No "
                    "coordinates, no lake-zone link, and no daily resolution. "
                    "Descriptive context only."
                ),
            },
            "note": (
                "PAGASA monthly station summaries; 2025 is partial and still "
                "undergoing verification. The Tanay card is a single-station "
                "regional proxy, not a lake measurement."
            ),
        },
        "events": event_rows,
        "evidenceAudit": audit_rows,
        "sources": source_rows,
        "dataRequests": request_summary,
        "figures": figure_rows,
        "governance": {
            "feasibility": feasibility,
            "readiness": readiness_rows,
            "trainingChecks": training_rows,
            "evaluationChecks": evaluation_rows,
            "modelStatus": (
                "Real-data training is blocked by the evidence gate. "
                "A descriptive annual trend estimate is available separately."
            ),
            "metricsAvailable": False,
            "realTrendAvailable": True,
        },
        "risk": {
            "status": "insufficient_data",
            "headline": "No valid model prediction available",
            "summary": "One reported event period, no pre-event daily observation, no credible negative windows, and no station-to-zone mapping.",
            "reasons": [
                "LLDA water quality is published as annual station summaries.",
                "PAGASA rainfall and wind are monthly station summaries.",
                "The single accepted event report has no pre-event dated sample.",
                "No station coordinates or authoritative zone map are supplied.",
                "Absence of a fish-kill report is not a verified non-event.",
            ],
        },
    }

    output_path = DATA_DIR / "dashboard.json"
    dashboard = sanitize(dashboard)
    output_path.write_text(
        json.dumps(dashboard, ensure_ascii=False, indent=2, allow_nan=False),
        encoding="utf-8",
    )
    print(f"Dashboard data: {output_path}")
    print(f"Lake stations: {coverage['lakeStations']}; measurements: {len(measurements)}")
    print(f"Figures copied: {len(figure_rows)} -> {PUBLIC_FIGURE_DIR}")


if __name__ == "__main__":
    main()
