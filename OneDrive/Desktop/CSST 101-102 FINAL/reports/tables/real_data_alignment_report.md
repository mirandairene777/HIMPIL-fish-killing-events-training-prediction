# Real-data alignment report

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
| Dissolved oxygen | 90 | -0.112 mg/L | -0.141 to -0.083 | -0.138 to -0.087 | decline |
| Water temperature | 81 | 0.056 deg C | -0.013 to 0.125 | -0.009 to 0.110 | no clear trend |

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
.\.venv\Scripts\python.exe python\train_real_trend.py
.\.venv\Scripts\python.exe python\build_dashboard_data.py
cd dashboard
npm run build
```
