# Annual water-quality trend model card

**Model:** station fixed-effects linear trend
**Status:** Real data, descriptive only
**Not:** a fish-kill prediction, a 72-hour model, a risk score, a zone map, or an advisory

## Intended use

Summarize the direction of annual lake-wide change in dissolved oxygen and water
temperature for the nine lake stations with a complete 2016-2025 record. The
estimate is a descriptive association for the evidence dashboard. It is not used
to generate a fish-kill label or a warning.

## Model

- **Panel:** 9 stations, 2016-2025
- **Method:** Ordinary least squares with station fixed effects and a common linear year term; HC3 standard errors; 1,000-replicate cluster bootstrap by station.
- **DO observations:** 90 station-years; n = 9 stations
- **Temperature observations:** 81 station-years; n = 9 stations
- **DO estimate:** -0.112 mg/L per year (95% CI -0.141 to -0.083; cluster bootstrap -0.138 to -0.087)
- **Temperature estimate:** 0.056 deg C per year (95% CI -0.013 to 0.125; cluster bootstrap -0.009 to 0.110)

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
.\.venv\Scripts\python.exe python\train_real_trend.py
```

**Warning:** This model card describes a descriptive annual trend. It is not
evidence that real fish kills are predictable, and it does not satisfy the
fish-kill model-readiness gate.
