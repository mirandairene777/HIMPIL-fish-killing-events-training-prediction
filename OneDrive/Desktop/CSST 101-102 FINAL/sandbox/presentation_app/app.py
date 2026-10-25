#!/usr/bin/env python
"""Local web demo for the synthetic five-input HIMPIL presentation model.

Synthetic demo only.

Run from the repository root:

    .\\.venv\\Scripts\\python.exe sandbox\\presentation_app\\app.py

Then open http://127.0.0.1:8000 in a browser. The app is deliberately separate
from the evidence dashboard and has no external dependencies.
"""

from __future__ import annotations

import argparse
import html
import json
import math
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs

APP_DIR = Path(__file__).resolve().parent
ROOT = APP_DIR.parents[1]
SYNTHETIC_DIR = ROOT / "sandbox" / "synthetic"
if str(SYNTHETIC_DIR) not in sys.path:
    sys.path.insert(0, str(SYNTHETIC_DIR))

from predict_presentation import (  # noqa: E402
    MANIFEST_PATH,
    MODEL_PATH,
    load_artifacts,
    predict_from_features,
)

FEATURES = [
    "do_mg_l",
    "water_temp_c",
    "ph",
    "rainfall_mm_mean",
    "wind_mps_mean",
]
FALLBACK_LABELS = {
    "do_mg_l": "Dissolved oxygen (mg/L)",
    "water_temp_c": "Water temperature (C)",
    "ph": "pH",
    "rainfall_mm_mean": "Rainfall (mm)",
    "wind_mps_mean": "Wind speed (m/s)",
}
EXAMPLE_VALUES = {
    "do_mg_l": 4.8,
    "water_temp_c": 30.0,
    "ph": 7.0,
    "rainfall_mm_mean": 15.0,
    "wind_mps_mean": 8.0,
}
RANGES = {
    "do_mg_l": (0.0, 30.0),
    "water_temp_c": (0.0, 45.0),
    "ph": (0.0, 14.0),
    "rainfall_mm_mean": (0.0, 1000.0),
    "wind_mps_mean": (0.0, 100.0),
}

CSS = """
:root {
  --bg: #0b1618;
  --panel: #122326;
  --panel-2: #173033;
  --ink: #e9f2ef;
  --muted: #9fb8b2;
  --line: #2a484b;
  --teal: #5fd0bd;
  --amber: #efb85a;
  --coral: #ef7d6f;
  --low: #5fd0bd;
  --medium: #efb85a;
  --high: #ef7d6f;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  background: radial-gradient(circle at top left, #143033 0, var(--bg) 42rem);
  color: var(--ink);
  font: 16px/1.5 "Segoe UI", Roboto, Arial, sans-serif;
}
.wrap { width: min(1080px, calc(100% - 2rem)); margin: 0 auto; padding: 1.5rem 0 3rem; }
.warning {
  border: 1px solid #7c5b23;
  background: #2a2111;
  color: #ffd792;
  padding: .8rem 1rem;
  border-radius: .6rem;
  font-weight: 700;
  letter-spacing: .04em;
}
header { margin: 1.4rem 0 1.2rem; }
h1 { font-size: clamp(1.8rem, 4vw, 3rem); line-height: 1.1; margin: 0 0 .5rem; }
h2 { font-size: 1.05rem; letter-spacing: .06em; text-transform: uppercase; color: var(--teal); margin: 0 0 .6rem; }
p { color: var(--muted); max-width: 70ch; }
.lede { font-size: 1.08rem; }
.grid { display: grid; grid-template-columns: minmax(0, 1.2fr) minmax(280px, .8fr); gap: 1rem; align-items: start; }
.panel { background: linear-gradient(180deg, var(--panel), var(--panel-2)); border: 1px solid var(--line); border-radius: .8rem; padding: 1.1rem; }
form { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: .8rem; }
.field { display: flex; flex-direction: column; gap: .3rem; }
.field:last-of-type { grid-column: 1 / -1; }
label { color: var(--muted); font-size: .9rem; }
input {
  width: 100%; padding: .7rem .8rem; border-radius: .45rem; border: 1px solid var(--line);
  background: #0d1c1e; color: var(--ink); font-size: 1rem;
}
input:focus { outline: 2px solid var(--teal); outline-offset: 2px; }
.actions { grid-column: 1 / -1; display: flex; gap: .6rem; flex-wrap: wrap; margin-top: .3rem; }
button {
  border: 0; border-radius: .45rem; padding: .75rem 1rem; font-size: .95rem;
  font-weight: 700; cursor: pointer;
}
button.primary { background: var(--teal); color: #06211d; }
button.secondary { background: transparent; color: var(--teal); border: 1px solid var(--line); }
button:hover { filter: brightness(1.08); }
.result { margin-top: 1rem; border-color: #3a6568; }
.probability { font-size: clamp(2.6rem, 8vw, 4.6rem); line-height: 1; font-weight: 800; margin: .4rem 0 .2rem; }
.band { display: inline-block; padding: .35rem .7rem; border-radius: 999px; font-weight: 800; letter-spacing: .03em; }
.band-low { background: #123b36; color: var(--low); border: 1px solid #2d756b; }
.band-medium { background: #3a2c12; color: var(--medium); border: 1px solid #80632d; }
.band-high { background: #3d1d1a; color: var(--high); border: 1px solid #8a4239; }
table { width: 100%; border-collapse: collapse; margin-top: .8rem; font-size: .92rem; }
th, td { text-align: left; padding: .45rem .3rem; border-bottom: 1px solid var(--line); vertical-align: top; }
th { color: var(--muted); font-weight: 600; }
.notice { border-left: 3px solid var(--amber); padding-left: .8rem; margin-top: 1rem; color: #e7cf9f; }
.error { border: 1px solid #8a4239; background: #321614; color: #ffb5aa; padding: .8rem 1rem; border-radius: .55rem; margin-top: 1rem; }
.small { font-size: .86rem; color: var(--muted); }
code { color: #cde9e2; }
ul { color: var(--muted); padding-left: 1.15rem; }
li { margin: .3rem 0; }
footer { margin-top: 1.4rem; color: var(--muted); font-size: .84rem; }
@media (max-width: 760px) {
  .grid { grid-template-columns: 1fr; }
  form { grid-template-columns: 1fr; }
  .field:last-of-type { grid-column: auto; }
}
"""

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>HIMPIL synthetic presentation demo</title>
<style>__CSS__</style>
</head>
<body>
<div class="wrap">
  <div class="warning">Synthetic demo</div>
  <header>
    <h1>HIMPIL five-input presentation demo</h1>
    <p class="lede">Enter hypothetical water-quality and weather values. The saved random forest returns a
    <strong>simulated 72-hour event probability</strong> and an illustrative demo band.</p>
  </header>
  __ERROR__
  <div class="grid">
    <section class="panel">
      <h2>Hypothetical inputs</h2>
      <form method="post" action="/predict">
        __FIELDS__
        <div class="actions">
          <button class="primary" type="submit">Run simulation</button>
          <button class="secondary" type="button" onclick="fillExample()">Load example values</button>
        </div>
      </form>
      <p class="small">The model uses exactly these five fields. Example values are fictional and are
      included only to show the interface. Changing the band thresholds changes the demo label.</p>
    </section>
    <aside class="panel">
      <h2>What this is</h2>
      <ul>
        <li>A trained model artifact loaded from <code>models/synthetic/presentation/</code>.</li>
        <li>A software and interface demonstration for the team.</li>
        <li>A way to show how the five requested inputs flow through a pipeline.</li>
      </ul>
      <h2>What this is not</h2>
      <ul>
        <li>Not real fish-kill prediction.</li>
        <li>Not real performance or a validated risk level.</li>
        <li>Not connected to the evidence dashboard.</li>
      </ul>
    </aside>
  </div>
  __RESULT__
  <footer>
    Target: synthetic 72-hour event start. Model: <code>risk_demo_model.joblib</code>.
    This app is separate from <code>dashboard/</code> and does not write risk data.
  </footer>
</div>
<script>
function fillExample() {
  const values = __EXAMPLE_JSON__;
  for (const [id, value] of Object.entries(values)) {
    const input = document.getElementById(id);
    if (input) input.value = value;
  }
}
</script>
</body>
</html>
"""

RESULT_TEMPLATE = """
<section class="panel result">
  <h2>Simulated output</h2>
  <div class="probability">__PERCENT__%</div>
  <div class="band __BAND_CLASS__">__BAND__ demo band</div>
  <p>Simulated probability that a synthetic event starts within 72 hours at this station:
  <strong>__PROBABILITY__</strong>.</p>
  <table>
    <thead><tr><th>Input</th><th>Value used</th></tr></thead>
    <tbody>__INPUT_ROWS__</tbody>
  </table>
  <p class="notice"><strong>Hypothetical input.</strong> This is a synthetic model output, not a real
  fish-kill risk assessment or advisory. Low/Medium/High are communication labels, not validated
  thresholds.</p>
</section>
"""


def format_input_value(value: object) -> str:
    return html.escape(str(value), quote=True)


def render_fields(values: dict[str, float], labels: dict[str, str]) -> str:
    parts = []
    for name in FEATURES:
        label = labels.get(name, FALLBACK_LABELS[name])
        low, high = RANGES[name]
        parts.append(
            f'<div class="field">'
            f'<label for="{name}">{html.escape(label)}</label>'
            f'<input id="{name}" name="{name}" type="number" step="any" '
            f'min="{low}" max="{high}" required value="{format_input_value(values.get(name, ""))}">'
            f"</div>"
        )
    return "\n".join(parts)


def render_result(result: dict[str, object], labels: dict[str, str]) -> str:
    probability = float(result["probability_72h"])
    demo_band = str(result["demo_band"])
    band_class = f"band-{demo_band.lower()}"
    inputs = result["inputs"]
    rows = []
    for name in FEATURES:
        label = labels.get(name, FALLBACK_LABELS[name])
        rows.append(
            f"<tr><td>{html.escape(label)}</td><td>{format_input_value(inputs[name])}</td></tr>"
        )
    return (
        RESULT_TEMPLATE.replace("__PERCENT__", f"{probability * 100:.1f}")
        .replace("__BAND_CLASS__", band_class)
        .replace("__BAND__", html.escape(demo_band))
        .replace("__PROBABILITY__", f"{probability:.4f}")
        .replace("__INPUT_ROWS__", "\n".join(rows))
    )


def render_page(
    labels: dict[str, str],
    values: dict[str, float] | None = None,
    result: dict[str, object] | None = None,
    error: str | None = None,
) -> str:
    values = values or dict(EXAMPLE_VALUES)
    error_html = f'<div class="error">{html.escape(error)}</div>' if error else ""
    result_html = render_result(result, labels) if result else ""
    return (
        PAGE.replace("__CSS__", CSS)
        .replace("__ERROR__", error_html)
        .replace("__FIELDS__", render_fields(values, labels))
        .replace("__RESULT__", result_html)
        .replace("__EXAMPLE_JSON__", json.dumps(EXAMPLE_VALUES))
    )


def parse_and_validate(body: bytes) -> tuple[dict[str, float] | None, str | None]:
    parsed = parse_qs(body.decode("utf-8", errors="replace"))
    values: dict[str, float] = {}
    for name in FEATURES:
        raw = (parsed.get(name) or [""])[0].strip()
        if not raw:
            return None, f"Missing value for {FALLBACK_LABELS[name]}."
        try:
            number = float(raw)
        except ValueError:
            return None, f"{FALLBACK_LABELS[name]} must be a number."
        if not math.isfinite(number):
            return None, f"{FALLBACK_LABELS[name]} must be finite."
        low, high = RANGES[name]
        if not (low <= number <= high):
            return None, f"{FALLBACK_LABELS[name]} must be between {low:g} and {high:g}."
        values[name] = number
    return values, None


class DemoHandler(BaseHTTPRequestHandler):
    model = None
    manifest: dict = {}

    def _send_html(self, body: str, status: int = 200) -> None:
        payload = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(payload)

    def _send_json(self, data: dict, status: int = 200) -> None:
        payload = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self) -> None:
        if self.path in ("/", "/index.html"):
            labels = self.manifest.get("feature_labels", {})
            self._send_html(render_page(labels))
            return
        if self.path == "/health":
            self._send_json({"status": "ok", "mode": "synthetic_demo"})
            return
        self._send_html("<h1>Not found</h1>", status=404)

    def do_POST(self) -> None:
        if self.path != "/predict":
            self._send_html("<h1>Not found</h1>", status=404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = 0
        body = self.rfile.read(max(0, min(length, 100_000)))
        values, error = parse_and_validate(body)
        labels = self.manifest.get("feature_labels", {})
        if error or values is None:
            self._send_html(render_page(labels, values=EXAMPLE_VALUES, error=error), status=400)
            return
        result = predict_from_features(self.model, self.manifest, values)
        self._send_html(render_page(labels, values=values, result=result))

    def log_message(self, fmt: str, *args: object) -> None:
        print(f"[demo] {self.address_string()} {fmt % args}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the local HIMPIL presentation demo.")
    parser.add_argument("--host", default="127.0.0.1", help="Bind address (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Port (default: 8000)")
    args = parser.parse_args()

    try:
        model, manifest = load_artifacts()
    except FileNotFoundError as exc:
        raise SystemExit(
            f"Missing model artifact: {exc}\n"
            "Run sandbox/synthetic/train_presentation_model.py first."
        ) from exc

    DemoHandler.model = model
    DemoHandler.manifest = manifest
    server = ThreadingHTTPServer((args.host, args.port), DemoHandler)
    url = f"http://{args.host}:{args.port}"
    print("Synthetic demo only.")
    print(f"Serving the five-input presentation demo at {url}")
    print(f"Model: {MODEL_PATH}")
    print(f"Manifest: {MANIFEST_PATH}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping demo.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
