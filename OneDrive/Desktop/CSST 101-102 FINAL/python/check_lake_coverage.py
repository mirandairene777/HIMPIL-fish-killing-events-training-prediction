"""
HIMPIL Phase 2 - lake station-year coverage check.

Reads the six Laguna de Bay water-quality workbooks and reports, for the 15
lake stations only, which variables are present for each station-year.

Outputs:
  reports/tables/lake_station_year_coverage.csv
  reports/tables/lake_coverage_summary.csv

Run:
    .venv\\Scripts\\python.exe python\\check_lake_coverage.py
"""

from __future__ import annotations

import csv
import re
from collections import Counter, defaultdict
from pathlib import Path

import openpyxl

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
TABLE_DIR = PROJECT_ROOT / "reports" / "tables"

VARIABLE_FILES = [
    ("Nitrate", "Nitrate"),
    ("Phosphate", "Phosphate"),
    ("BOD", "Biochemical oxygen demand (BOD)"),
    ("pH", "pH"),
    ("Temperature", "Water temperature"),
    ("DO", "Dissolved oxygen (DO)"),
]
YEARS = list(range(2016, 2026))
MISSING_SYMBOLS = {"...", "\u2026", "**", "\ufffd", "—", "–", ""}


def is_number(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def read_lake_data(path: Path):
    """Return {station: {variable: {year: value}}} for one workbook."""
    workbook = openpyxl.load_workbook(path, data_only=True)
    sheet = workbook.worksheets[0]
    header_row = None
    for row in range(1, min(sheet.max_row, 30) + 1):
        if str(sheet.cell(row, 1).value).strip().lower() == "station":
            header_row = row
            break
    if header_row is None:
        raise ValueError(f"No Station header in {path.name}")

    year_columns = {}
    for col in range(2, sheet.max_column + 1):
        value = sheet.cell(header_row, col).value
        if isinstance(value, (int, float)) and 1900 <= value <= 2100:
            year_columns[int(value)] = col

    variable = next((v for needle, v in VARIABLE_FILES if needle in path.name), path.stem)
    data = defaultdict(dict)
    in_lake = False
    for row in range(header_row + 1, sheet.max_row + 1):
        name = sheet.cell(row, 1).value
        if name is None:
            continue
        name = re.sub(r"\s+", " ", str(name)).strip()
        low = name.lower()
        if low.startswith(("notes", "source", "data as of")):
            break
        if low == "laguna de bay":
            in_lake = True
            continue
        if low == "major tributaries":
            break
        if low in {"ncr", "laguna", "rizal"} or low.startswith("region "):
            continue
        if not in_lake:
            continue
        for year, col in year_columns.items():
            data[name][year] = sheet.cell(row, col).value
    workbook.close()
    return variable, data


def main():
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    all_data = {}
    for needle, _ in VARIABLE_FILES:
        candidates = [p for p in RAW_DIR.glob("*.xlsx") if needle in p.name]
        if len(candidates) != 1:
            raise SystemExit(f"Expected exactly one workbook matching {needle!r}")
        variable, data = read_lake_data(candidates[0])
        all_data[variable] = data

    stations = sorted({station for data in all_data.values() for station in data})
    variables = [label for _, label in VARIABLE_FILES]

    detail_rows = []
    complete_count = 0
    for station in stations:
        for year in YEARS:
            present = []
            missing = []
            for variable in variables:
                value = all_data[variable].get(station, {}).get(year)
                if is_number(value):
                    present.append(variable)
                else:
                    missing.append(variable)
            complete = len(missing) == 0
            complete_count += complete
            detail_rows.append({
                "station": station,
                "year": year,
                "variables_present": len(present),
                "complete_all_six": "yes" if complete else "no",
                "missing_variables": " | ".join(missing),
            })

    summary_rows = []
    for variable in variables:
        values = [v for data in [all_data[variable]] for station in data
                  for v in data[station].values()]
        numeric = sum(1 for value in values if is_number(value))
        summary_rows.append({
            "measure": variable,
            "potential_lake_station_years": len(stations) * len(YEARS),
            "numeric_values": numeric,
            "missing_values": len(values) - numeric,
            "complete_percent": round(100 * numeric / len(values), 2) if values else 0,
        })

    summary_rows.append({
        "measure": "All six variables simultaneously",
        "potential_lake_station_years": len(stations) * len(YEARS),
        "numeric_values": complete_count,
        "missing_values": len(stations) * len(YEARS) - complete_count,
        "complete_percent": round(100 * complete_count / (len(stations) * len(YEARS)), 2),
    })

    with (TABLE_DIR / "lake_station_year_coverage.csv").open(
        "w", newline="", encoding="utf-8-sig"
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=list(detail_rows[0]))
        writer.writeheader()
        writer.writerows(detail_rows)

    with (TABLE_DIR / "lake_coverage_summary.csv").open(
        "w", newline="", encoding="utf-8-sig"
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=list(summary_rows[0]))
        writer.writeheader()
        writer.writerows(summary_rows)

    print("Lake coverage check complete")
    print(f"Lake stations: {len(stations)}")
    print(f"Potential lake station-years: {len(stations) * len(YEARS)}")
    print(f"Complete across all six variables: {complete_count}")
    print("\nPer-variable numeric lake station-years:")
    for row in summary_rows[:-1]:
        print(f"  {row['measure']}: {row['numeric_values']} / "
              f"{row['potential_lake_station_years']} ({row['complete_percent']}%)")
    print("\nCoverage by station-year is in "
          "reports/tables/lake_station_year_coverage.csv")

    # Show structural missingness, not just totals.
    missing_by_year = Counter()
    for row in detail_rows:
        if row["complete_all_six"] == "no":
            missing_by_year[row["year"]] += 1
    print("Incomplete station-years by year:")
    for year in YEARS:
        print(f"  {year}: {missing_by_year.get(year, 0)} incomplete")


if __name__ == "__main__":
    main()
