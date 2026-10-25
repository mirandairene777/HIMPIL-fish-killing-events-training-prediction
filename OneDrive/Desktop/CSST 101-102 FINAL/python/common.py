"""Shared paths and small helpers for the HIMPIL data pipeline.

Nothing in this module changes a source file. All outputs are written under
data/processed or reports/.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
SOURCE_DOC_DIR = RAW_DIR / "source_documents"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_DIR = PROJECT_ROOT / "data" / "outputs"
TABLE_DIR = PROJECT_ROOT / "reports" / "tables"
FIGURE_DIR = PROJECT_ROOT / "reports" / "figures"
MODEL_DIR = PROJECT_ROOT / "models"
DOC_TEXT_DIR = PROCESSED_DIR / "source_text"

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

MONTH_NUMBER = {name: index for index, name in enumerate(MONTHS, start=1)}

# Canonical variable names, units and broad plausibility bounds.
# These bounds only flag obvious data-entry errors; they are not regulatory
# thresholds and are not used to create labels.
VARIABLES = {
    "nitrate": {
        "name": "Nitrate",
        "unit": "mg/L",
        "low": 0.0,
        "high": 100.0,
        "workbook_key": "1.32",
    },
    "phosphate": {
        "name": "Phosphate",
        "unit": "mg/L",
        "low": 0.0,
        "high": 100.0,
        "workbook_key": "1.33",
    },
    "bod": {
        "name": "BOD",
        "unit": "mg/L",
        "low": 0.0,
        "high": 1000.0,
        "workbook_key": "1.34.2",
    },
    "ph": {
        "name": "pH",
        "unit": "pH units",
        "low": 0.0,
        "high": 14.0,
        "workbook_key": "1.37",
    },
    "temperature": {
        "name": "Water temperature",
        "unit": "deg C",
        "low": 0.0,
        "high": 50.0,
        "workbook_key": "1.38",
    },
    "do": {
        "name": "Dissolved oxygen (DO)",
        "unit": "mg/L",
        "low": 0.0,
        "high": 25.0,
        "workbook_key": "1.39.2",
    },
}

WATER_QUALITY_KEYS = list(VARIABLES)
WEATHER_SPECS = {
    "rainfall": {
        "name": "Rainfall",
        "unit": "mm",
        "workbook_key": "1.2 Amount",
    },
    "wind": {
        "name": "Wind speed",
        "unit": "m/s",
        "workbook_key": "1.6 Wind",
    },
}

EVENT_COLUMNS = [
    "event_id",
    "event_start_date",
    "event_end_date",
    "location",
    "municipality",
    "lake_zone",
    "fish_species",
    "estimated_fish_losses",
    "estimated_economic_loss",
    "reported_cause",
    "source_title",
    "source_url",
    "publication_date",
    "date_precision",
    "location_precision",
    "verification_status",
    "notes",
]


def ensure_dirs() -> None:
    for path in (PROCESSED_DIR, OUTPUT_DIR, TABLE_DIR, FIGURE_DIR, MODEL_DIR, DOC_TEXT_DIR):
        path.mkdir(parents=True, exist_ok=True)


def text(value) -> str:
    """Return a trimmed, single-line string; None becomes an empty string."""
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def normalise_name(value) -> str:
    return re.sub(r"\s+", " ", text(value)).casefold()


def is_number(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def write_csv(path: Path, rows: list[dict], fieldnames: list[str] | None = None) -> None:
    """Write a CSV with a header even when there are no data rows."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        fieldnames = list(rows[0].keys()) if rows else []
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path: Path) -> list[dict]:
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def find_workbook(workbook_key: str) -> Path:
    """Locate a workbook by a distinctive part of its filename."""
    matches = sorted(RAW_DIR.glob(f"*{workbook_key}*.xlsx"))
    if len(matches) != 1:
        raise FileNotFoundError(
            f"Expected exactly one workbook matching *{workbook_key}*.xlsx, found {len(matches)}"
        )
    return matches[0]


def missing_kind(value) -> str:
    """Classify a non-numeric cell without inventing a value."""
    raw = text(value)
    if raw == "":
        return "blank"
    if raw == "**":
        return "station_discontinued"
    if raw in {"\u2026", "\ufffd", "\u2014", "\u2013", "-"}:
        return "no_data_symbol"
    if raw == "...":
        return "ellipsis_undefined"
    return "other_non_numeric"


def as_float(value) -> float | None:
    if is_number(value):
        return float(value)
    return None


def year_from_header(value) -> int | None:
    if is_number(value) and float(value).is_integer() and 1900 <= int(value) <= 2100:
        return int(value)
    return None


def markdown_table(rows: list[dict], columns: list[tuple[str, str]]) -> str:
    """Render a compact Markdown table from a list of dicts."""
    header = "| " + " | ".join(label for _, label in columns) + " |"
    rule = "|" + "|".join("---" for _ in columns) + "|"
    lines = [header, rule]
    for row in rows:
        cells = []
        for key, _ in columns:
            value = text(row.get(key, ""))
            cells.append(value.replace("|", "/"))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)
