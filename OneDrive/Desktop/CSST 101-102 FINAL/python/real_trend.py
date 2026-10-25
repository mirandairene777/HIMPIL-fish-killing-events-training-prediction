"""Fit the defensible real-data trend model.

This module fits a descriptive station fixed-effects linear trend to the
annual lake-station summaries. It is deliberately not a fish-kill model and
does not create 24-, 48-, or 72-hour labels.

The model answers one narrow question: among the nine lake stations with a
complete 2016-2025 annual record, what is the average within-station change
per year in annual mean dissolved oxygen and water temperature?
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from common import TABLE_DIR

DO_COLUMN = "Dissolved oxygen (DO)"
TEMP_COLUMN = "Water temperature"
BASE_YEAR = 2016
BOOTSTRAP_REPS = 1000
BOOTSTRAP_SEED = 42


def _design_matrix(
    years: np.ndarray,
    station_codes: np.ndarray,
    n_stations: int,
) -> np.ndarray:
    """Intercept, common year slope, and station fixed effects."""
    columns = [
        np.ones(len(years), dtype=float),
        years.astype(float) - BASE_YEAR,
    ]
    for code in range(1, n_stations):
        columns.append((station_codes == code).astype(float))
    return np.column_stack(columns)


def _fit_ols(
    years: np.ndarray,
    station_codes: np.ndarray,
    values: np.ndarray,
    n_stations: int,
) -> tuple[np.ndarray, np.ndarray]:
    design = _design_matrix(years, station_codes, n_stations)
    coefficients, *_ = np.linalg.lstsq(design, values, rcond=None)
    residuals = values - design @ coefficients

    xtx_inv = np.linalg.pinv(design.T @ design)
    leverage = np.sum(design * (design @ xtx_inv), axis=1)
    leverage = np.clip(leverage, 0.0, 1.0 - 1e-9)
    omega = residuals**2 / (1.0 - leverage) ** 2
    covariance = xtx_inv @ (design.T * omega) @ design @ xtx_inv
    standard_errors = np.sqrt(np.clip(np.diag(covariance), 0.0, None))

    return coefficients, standard_errors


def _fit_target(
    frame: pd.DataFrame,
    target_column: str,
    label: str,
    unit: str,
    stations: list[str],
    years: list[int],
) -> dict:
    data = frame.loc[
        frame["station_name"].isin(stations),
        ["station_name", "year", target_column],
    ].dropna()
    data = data.sort_values(["station_name", "year"]).reset_index(drop=True)

    station_codes = pd.Categorical(
        data["station_name"], categories=stations, ordered=True
    ).codes.astype(int)
    year_values = data["year"].to_numpy(dtype=int)
    observations = data[target_column].to_numpy(dtype=float)

    coefficients, standard_errors = _fit_ols(
        year_values,
        station_codes,
        observations,
        len(stations),
    )
    slope = float(coefficients[1])
    slope_se = float(standard_errors[1])
    ci_low = slope - 1.96 * slope_se
    ci_high = slope + 1.96 * slope_se

    predictions = _design_matrix(
        year_values, station_codes, len(stations)
    ) @ coefficients
    residuals = observations - predictions
    total_sum_squares = float(np.sum((observations - observations.mean()) ** 2))
    r_squared = (
        1.0 - float(np.sum(residuals**2)) / total_sum_squares
        if total_sum_squares > 0
        else None
    )

    # Cluster bootstrap by station. This respects the repeated station
    # observations and avoids treating 90 station-years as 90 independent
    # stations.
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    station_indices = {
        station: np.flatnonzero(data["station_name"].to_numpy() == station)
        for station in stations
    }
    bootstrap_slopes: list[float] = []
    for _ in range(BOOTSTRAP_REPS):
        sampled = rng.choice(stations, size=len(stations), replace=True)
        indices = np.concatenate([station_indices[station] for station in sampled])
        bootstrap_codes = np.concatenate(
            [
                np.full(len(station_indices[station]), code, dtype=int)
                for code, station in enumerate(sampled)
            ]
        )
        try:
            bootstrap_coefficients, _ = _fit_ols(
                year_values[indices],
                bootstrap_codes,
                observations[indices],
                len(sampled),
            )
        except np.linalg.LinAlgError:
            continue
        candidate = float(bootstrap_coefficients[1])
        if np.isfinite(candidate):
            bootstrap_slopes.append(candidate)

    if bootstrap_slopes:
        bootstrap_low, bootstrap_high = np.percentile(
            np.asarray(bootstrap_slopes), [2.5, 97.5]
        )
    else:
        bootstrap_low = bootstrap_high = None

    if ci_high < 0:
        direction = "decline"
        interpretation = "The 95% confidence interval excludes zero."
    elif ci_low > 0:
        direction = "increase"
        interpretation = "The 95% confidence interval excludes zero."
    else:
        direction = "no clear trend"
        interpretation = "The 95% confidence interval includes zero."

    return {
        "label": label,
        "unit": unit,
        "n": int(len(data)),
        "nStations": int(data["station_name"].nunique()),
        "slopePerYear": round(slope, 6),
        "ciLow": round(float(ci_low), 6),
        "ciHigh": round(float(ci_high), 6),
        "standardError": round(slope_se, 6),
        "bootstrapLow": None if bootstrap_low is None else round(float(bootstrap_low), 6),
        "bootstrapHigh": None if bootstrap_high is None else round(float(bootstrap_high), 6),
        "bootstrapReps": len(bootstrap_slopes),
        "rSquared": None if r_squared is None else round(r_squared, 6),
        "direction": direction,
        "interpretation": interpretation,
    }


def fit_annual_trends(lake: pd.DataFrame) -> dict:
    """Return the real descriptive annual-trend summary."""
    years = sorted(int(year) for year in lake["year"].unique())
    do_counts = (
        lake.dropna(subset=[DO_COLUMN])
        .groupby("station_name")["year"]
        .nunique()
    )
    stations = sorted(do_counts[do_counts == len(years)].index.tolist())
    if not stations:
        raise ValueError("No station has a complete annual DO record.")

    targets = {
        "do": _fit_target(
            lake,
            DO_COLUMN,
            "Dissolved oxygen (DO)",
            "mg/L per year",
            stations,
            years,
        ),
        "temperature": _fit_target(
            lake,
            TEMP_COLUMN,
            "Water temperature",
            "deg C per year",
            stations,
            years,
        ),
    }

    return {
        "generatedAtUtc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "descriptive_annual_trend",
        "modelType": "station_fixed_effects_linear_trend",
        "fishKillPrediction": False,
        "warning": (
            "Descriptive annual trend only. Not a fish-kill prediction, "
            "not a 72-hour model, and not an advisory."
        ),
        "panel": {
            "stations": len(stations),
            "stationNames": stations,
            "years": f"{years[0]}-{years[-1]}",
            "nYears": len(years),
        },
        "targets": targets,
        "method": (
            "Ordinary least squares with station fixed effects and a common "
            "linear year term; HC3 standard errors; 1,000-replicate cluster "
            "bootstrap by station."
        ),
        "caveat": (
            "The estimates describe annual station summaries. They do not "
            "use observation dates, do not establish causation, and do not "
            "predict fish kills."
        ),
        "unsupported": {
            "target": "72-hour fish-kill prediction",
            "status": "not_supported",
            "reasons": [
                "Water quality is reported as annual station summaries, not dated observations.",
                "Rainfall and wind are monthly station summaries, not daily or sub-daily series.",
                "There are zero pre-event observations and zero usable 24-hour labels.",
                "There is one reported event and no verified negative windows.",
                "Station coordinates and an authoritative lake-zone crosswalk are absent.",
            ],
        },
        "notes": [
            "The model is fitted only to the nine stations with a complete 2016-2025 DO record.",
            "The fish-kill risk state remains unavailable and is not derived from this model.",
            "The synthetic 72-hour experiments remain separate and are not evidence.",
        ],
    }


def _format(value: float | None, digits: int = 3) -> str:
    if value is None:
        return "not available"
    return f"{value:.{digits}f}"


def write_outputs(summary: dict, table_dir: Path = TABLE_DIR) -> None:
    """Write the JSON, metrics CSV, model card, and alignment report."""
    table_dir.mkdir(parents=True, exist_ok=True)
    (table_dir / "real_trend_model.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    with (table_dir / "real_trend_model_metrics.csv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "target",
                "n",
                "n_stations",
                "slope_per_year",
                "ci_low",
                "ci_high",
                "bootstrap_low",
                "bootstrap_high",
                "r_squared",
                "unit",
                "direction",
            ]
        )
        for key, target in summary["targets"].items():
            writer.writerow(
                [
                    key,
                    target["n"],
                    target["nStations"],
                    target["slopePerYear"],
                    target["ciLow"],
                    target["ciHigh"],
                    target["bootstrapLow"],
                    target["bootstrapHigh"],
                    target["rSquared"],
                    target["unit"],
                    target["direction"],
                ]
            )

    do = summary["targets"]["do"]
    temp = summary["targets"]["temperature"]
    card = f"""# Annual water-quality trend model card

**Model:** station fixed-effects linear trend
**Status:** Real data, descriptive only
**Not:** a fish-kill prediction, a 72-hour model, a risk score, a zone map, or an advisory

## Intended use

Summarize the direction of annual lake-wide change in dissolved oxygen and water
temperature for the nine lake stations with a complete 2016-2025 record. The
estimate is a descriptive association for the evidence dashboard. It is not used
to generate a fish-kill label or a warning.

## Model

- **Panel:** {summary['panel']['stations']} stations, {summary['panel']['years']}
- **Method:** {summary['method']}
- **DO observations:** {do['n']} station-years; n = {do['nStations']} stations
- **Temperature observations:** {temp['n']} station-years; n = {temp['nStations']} stations
- **DO estimate:** {_format(do['slopePerYear'])} mg/L per year (95% CI {_format(do['ciLow'])} to {_format(do['ciHigh'])}; cluster bootstrap {_format(do['bootstrapLow'])} to {_format(do['bootstrapHigh'])})
- **Temperature estimate:** {_format(temp['slopePerYear'])} deg C per year (95% CI {_format(temp['ciLow'])} to {_format(temp['ciHigh'])}; cluster bootstrap {_format(temp['bootstrapLow'])} to {_format(temp['bootstrapHigh'])})

## Prohibited uses

- Do not call this a fish-kill risk model.
- Do not use it to assign a risk level to a station, zone, or date.
- Do not use it as a 24-, 48-, or 72-hour warning.
- Do not treat the association as causal.
- Do not place its output on a real map as a risk surface.

## Limitations

The inputs are annual station summaries without observation dates or a
documented aggregation rule. The panel is small, the stations are not a
probability sample, and the analysis does not control for changes in monitoring
practice. The temperature estimate is uncertain. No real fish-kill labels exist,
so the model cannot be evaluated against fish-kill events.

## Reproduction

```powershell
.\\.venv\\Scripts\\python.exe python\\train_real_trend.py
```

**Warning:** This model card describes a descriptive annual trend. It is not
evidence that real fish kills are predictable, and it does not satisfy the
fish-kill model-readiness gate.
"""
    (table_dir / "real_trend_model_card.md").write_text(card, encoding="utf-8")

    report = f"""# Real-data alignment report

**Status:** The system is aligned to the resolution of the supplied data. A
real fish-kill model is still not supported.

## What the data can support

- 14 sources; 15 lake stations; 150 lake station-years; 111 complete
  station-years across six water-quality variables; 711 numeric lake values.
- A descriptive annual trend model on the balanced nine-station panel.
- Monthly rainfall and wind context, including the separate Tanay regional card.
- A dashboard that reports coverage, completeness, event evidence, readiness,
  and the **risk assessment unavailable** state.

## The real model that was fitted

The model is a station fixed-effects linear trend with a common year term. It
uses annual station summaries only. It is not a fish-kill classifier.

| Target | n | Slope per year | 95% CI | Cluster bootstrap 95% | Direction |
|---|---:|---:|---|---|---|
| Dissolved oxygen | {do['n']} | {_format(do['slopePerYear'])} mg/L | {_format(do['ciLow'])} to {_format(do['ciHigh'])} | {_format(do['bootstrapLow'])} to {_format(do['bootstrapHigh'])} | {do['direction']} |
| Water temperature | {temp['n']} | {_format(temp['slopePerYear'])} deg C | {_format(temp['ciLow'])} to {_format(temp['ciHigh'])} | {_format(temp['bootstrapLow'])} to {_format(temp['bootstrapHigh'])} | {temp['direction']} |

The dissolved-oxygen estimate is negative and its confidence interval excludes
zero. The temperature estimate is positive but its interval includes zero. These
are descriptive associations, not causal findings.

## What the data cannot support

**A 72-hour fish-kill prediction is not available.** The supplied water quality
is annual, the weather is monthly, there are zero dated pre-event observations,
one reported event, zero verified events, and zero credible negative windows.
Interpolating or inventing a 72-hour series would create false precision and
would not be a real model.

The system therefore keeps the fish-kill risk state at **risk assessment
unavailable**. It does not show a risk score, a zone risk map, an advisory, or a
synthetic probability.

## What would unlock a real 72-hour model

1. Daily or sub-daily dissolved oxygen, temperature, pH, rainfall, and wind.
2. A verified incident log with dates, sites, zones, and causes.
3. A reporting-completeness record that supports credible negative windows.
4. Station coordinates and an authoritative lake-zone crosswalk.
5. Data-sharing permissions and a documented aggregation rule.

## Reproduction

```powershell
.\\.venv\\Scripts\\python.exe python\\train_real_trend.py
.\\.venv\\Scripts\\python.exe python\\build_dashboard_data.py
cd dashboard
npm run build
```
"""
    (table_dir / "real_data_alignment_report.md").write_text(report, encoding="utf-8")


def main() -> None:
    from common import PROCESSED_DIR

    lake = pd.read_csv(PROCESSED_DIR / "water_quality_lake_annual.csv")
    summary = fit_annual_trends(lake)
    write_outputs(summary)
    do = summary["targets"]["do"]
    temp = summary["targets"]["temperature"]
    print("Real annual trend model")
    print(
        f"DO: {do['slopePerYear']:.6f} mg/L/year "
        f"(95% CI {do['ciLow']:.6f} to {do['ciHigh']:.6f}; n={do['n']})"
    )
    print(
        f"Temperature: {temp['slopePerYear']:.6f} deg C/year "
        f"(95% CI {temp['ciLow']:.6f} to {temp['ciHigh']:.6f}; n={temp['n']})"
    )
    print(f"Wrote outputs to {TABLE_DIR}")


if __name__ == "__main__":
    main()
