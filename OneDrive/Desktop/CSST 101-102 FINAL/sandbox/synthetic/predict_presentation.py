#!/usr/bin/env python
"""Run the synthetic five-input presentation model for one hypothetical input.

SIMULATION ONLY - NOT EVIDENCE

Example:

    .\\.venv\\Scripts\\python.exe sandbox\\synthetic\\predict_presentation.py `
        --do 4.8 --temp 30 --ph 7.0 --rain 15 --wind 8

The output is a simulated 72-hour event probability and an illustrative
Low/Medium/High demo band. It is not a real fish-kill risk assessment.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
MODEL_DIR = ROOT / "models" / "synthetic" / "presentation"
MODEL_PATH = MODEL_DIR / "risk_demo_model.joblib"
MANIFEST_PATH = MODEL_DIR / "manifest.json"
WARNING = "SIMULATION ONLY - NOT EVIDENCE"


def band(probability: float, thresholds: dict[str, object]) -> str:
    low_max = float(thresholds["low_max"])
    high_min = float(thresholds["high_min"])
    if probability < low_max:
        return "Low"
    if probability < high_min:
        return "Medium"
    return "High"


def load_artifacts():
    """Load the saved model and its manifest once."""
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    model = joblib.load(MODEL_PATH)
    return model, manifest


def predict_from_features(
    model, manifest: dict, features: dict[str, float]
) -> dict[str, object]:
    """Return one simulated prediction from a feature-name/value mapping."""
    ordered = [float(features[name]) for name in manifest["features"]]
    input_frame = pd.DataFrame([ordered], columns=manifest["features"])
    probability = float(model.predict_proba(input_frame)[0, 1])
    demo_band = band(
        probability,
        manifest.get("band_thresholds", {"low_max": 0.25, "high_min": 0.50}),
    )
    return {
        "warning": WARNING,
        "data_origin": manifest["data_origin"],
        "target": manifest["target"],
        "inputs": {name: float(features[name]) for name in manifest["features"]},
        "probability_72h": round(probability, 6),
        "demo_band": demo_band,
        "note": (
            "Hypothetical input. This is a synthetic model output, not a real "
            "fish-kill risk assessment."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the synthetic five-input HIMPIL presentation model."
    )
    parser.add_argument("--do", type=float, required=True, help="Dissolved oxygen (mg/L)")
    parser.add_argument("--temp", type=float, required=True, help="Water temperature (C)")
    parser.add_argument("--ph", type=float, required=True, help="pH")
    parser.add_argument("--rain", type=float, required=True, help="Rainfall (mm)")
    parser.add_argument("--wind", type=float, required=True, help="Wind speed (m/s)")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the result as JSON instead of a short text report.",
    )
    args = parser.parse_args()

    model, manifest = load_artifacts()
    values = [args.do, args.temp, args.ph, args.rain, args.wind]
    features = dict(zip(manifest["features"], values))
    result = predict_from_features(model, manifest, features)

    if args.json:
        print(json.dumps(result, indent=2))
        return

    print(WARNING)
    print("Hypothetical input; not a real measurement.")
    print(f"  DO: {args.do} mg/L | Temp: {args.temp} C | pH: {args.ph}")
    print(f"  Rain: {args.rain} mm | Wind: {args.wind} m/s")
    print(f"  Simulated p(event within 72h): {result['probability_72h']:.4f}")
    print(f"  Illustrative demo band: {result['demo_band']}")
    print("  Not a real risk level, advisory, or early warning.")


if __name__ == "__main__":
    main()
