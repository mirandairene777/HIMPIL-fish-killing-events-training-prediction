# HIMPIL Phase 7b - descriptive environmental trends in R
#
# These are descriptive linear and Kendall trends through annual summaries.
# They are not causal estimates and they are not fish-kill model features.
#
# Run from anywhere:
#   "C:\Program Files\R\R-4.6.1\bin\Rscript.exe" r/environmental_trends.R

suppressPackageStartupMessages({
  library(readr)
  library(dplyr)
  library(tidyr)
  library(ggplot2)
  library(scales)
})

script_arg <- grep("^--file=", commandArgs(trailingOnly = FALSE), value = TRUE)
script_dir <- if (length(script_arg)) {
  dirname(normalizePath(sub("^--file=", "", script_arg[[1]])))
} else {
  getwd()
}
root <- normalizePath(file.path(script_dir, ".."))
processed <- file.path(root, "data", "processed")
tables <- file.path(root, "reports", "tables")
figures <- file.path(root, "reports", "figures")
dir.create(tables, recursive = TRUE, showWarnings = FALSE)
dir.create(figures, recursive = TRUE, showWarnings = FALSE)

numeric_flags <- c("ok", "out_of_range")

theme_set(
  theme_minimal(base_size = 11) +
    theme(
      panel.grid.minor = element_blank(),
      plot.title.position = "plot",
      plot.caption.position = "plot",
      strip.text = element_text(face = "bold"),
      legend.position = "bottom"
    )
)

wq_long <- read_csv(file.path(processed, "water_quality_long.csv"),
                    show_col_types = FALSE)
rain <- read_csv(file.path(processed, "rainfall_monthly.csv"),
                 show_col_types = FALSE)
wind <- read_csv(file.path(processed, "wind_monthly.csv"),
                 show_col_types = FALSE)

lake_numeric <- wq_long |>
  filter(station_type == "lake", quality_flag %in% numeric_flags, !is.na(value))

# ---------------------------------------------------------------------------
# Annual network summaries
# ---------------------------------------------------------------------------

network_annual <- lake_numeric |>
  group_by(year, variable, unit) |>
  summarise(
    n_stations = n(),
    mean = mean(value),
    sd = sd(value),
    se = sd / sqrt(n_stations),
    median = median(value),
    minimum = min(value),
    maximum = max(value),
    .groups = "drop"
  ) |>
  mutate(across(c(mean, sd, se, median, minimum, maximum), \(x) round(x, 5)))

write_csv(network_annual, file.path(tables, "r_water_quality_network_annual.csv"))

# ---------------------------------------------------------------------------
# Station-level annual trends
# ---------------------------------------------------------------------------

trend_one <- function(data) {
  n <- nrow(data)
  if (n < 5 || sd(data$value) == 0) {
    return(tibble(
      n_years = n,
      first_year = min(data$year),
      last_year = max(data$year),
      slope_per_year = NA_real_,
      slope_p_value = NA_real_,
      r_squared = NA_real_,
      kendall_tau = NA_real_,
      kendall_p_value = NA_real_
    ))
  }
  fit <- lm(value ~ year, data = data)
  coefs <- summary(fit)$coefficients
  slope <- if ("year" %in% rownames(coefs)) coefs["year", "Estimate"] else NA_real_
  slope_p <- if ("year" %in% rownames(coefs)) coefs["year", "Pr(>|t|)"] else NA_real_
  kt <- suppressWarnings(cor.test(data$year, data$value, method = "kendall", exact = FALSE))
  tibble(
    n_years = n,
    first_year = min(data$year),
    last_year = max(data$year),
    slope_per_year = unname(slope),
    slope_p_value = unname(slope_p),
    r_squared = summary(fit)$r.squared,
    kendall_tau = unname(kt$estimate),
    kendall_p_value = kt$p.value
  )
}

station_trends <- lake_numeric |>
  group_by(variable, unit, station_name, reported_lake_zone) |>
  group_modify(~ trend_one(.x)) |>
  ungroup() |>
  group_by(variable) |>
  mutate(slope_p_adj_bh = p.adjust(slope_p_value, method = "BH")) |>
  ungroup() |>
  arrange(variable, slope_p_value)

write_csv(station_trends, file.path(tables, "r_water_quality_station_trends.csv"))

# ---------------------------------------------------------------------------
# Water-quality trend figures
# ---------------------------------------------------------------------------

network_nutrients <- network_annual |>
  filter(variable %in% c("Nitrate", "Phosphate", "BOD"))

p_nutrients <- ggplot(network_nutrients, aes(x = year)) +
  geom_ribbon(aes(ymin = minimum, ymax = maximum), fill = "#a1d99b", alpha = 0.30) +
  geom_line(aes(y = mean), colour = "#006d2c", linewidth = 0.9) +
  geom_point(aes(y = mean), colour = "#006d2c", size = 2) +
  facet_wrap(~ variable, scales = "free_y", nrow = 1) +
  scale_x_continuous(breaks = 2016:2025) +
  labs(
    title = "Station-network annual nutrient and BOD values",
    subtitle = "Line is the unweighted station mean; ribbon is the station minimum-maximum range",
    x = "Year", y = "mg/L",
    caption = "Not a lake-wide areal estimate. The stations are fixed monitoring sites, not a probability sample."
  ) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1))

ggsave(file.path(figures, "fig_network_nutrients_trend.png"), p_nutrients,
       width = 12, height = 5, dpi = 150)

do_data <- lake_numeric |>
  filter(variable == "Dissolved oxygen (DO)")
do_network <- network_annual |>
  filter(variable == "Dissolved oxygen (DO)")

p_do <- ggplot(do_data, aes(x = year, y = value)) +
  geom_line(aes(group = station_name), colour = "grey70", linewidth = 0.45) +
  geom_point(colour = "grey60", size = 0.9, alpha = 0.7) +
  geom_line(data = do_network, aes(y = mean), colour = "#08519c", linewidth = 1.1) +
  geom_point(data = do_network, aes(y = mean), colour = "#08519c", size = 2.4) +
  geom_hline(yintercept = 5.0, linetype = "dashed", colour = "#b2182b") +
  scale_x_continuous(breaks = 2016:2025) +
  labs(
    title = "Dissolved oxygen: station trajectories and network mean",
    subtitle = "Grey lines are individual lake stations; blue is the unweighted station mean",
    x = "Year", y = "Dissolved oxygen (mg/L)",
    caption = "Annual station summaries. The 5.0 mg/L line is the reference cited in the 2019 UPD article."
  )

ggsave(file.path(figures, "fig_network_do_trend.png"), p_do,
       width = 10, height = 5.6, dpi = 150)

temp_network <- network_annual |>
  filter(variable == "Water temperature")

p_temp <- ggplot(temp_network, aes(x = year)) +
  geom_ribbon(aes(ymin = minimum, ymax = maximum), fill = "#fdae6b", alpha = 0.25) +
  geom_line(aes(y = mean), colour = "#a63603", linewidth = 0.9) +
  geom_point(aes(y = mean), colour = "#a63603", size = 2) +
  scale_x_continuous(breaks = 2016:2025) +
  labs(
    title = "Water temperature: network mean and station range",
    subtitle = "The 2017 gap reflects missing temperature values in all long-running lake stations",
    x = "Year", y = "Water temperature (deg C)",
    caption = "Annual station summaries; no observation dates are available."
  )

ggsave(file.path(figures, "fig_network_temperature_trend.png"), p_temp,
       width = 9, height = 5.2, dpi = 150)

# ---------------------------------------------------------------------------
# Weather annual summaries and trends
# ---------------------------------------------------------------------------

rain_annual <- rain |>
  filter(quality_flag %in% numeric_flags, !is.na(value), year <= 2024) |>
  group_by(station_name, year) |>
  summarise(
    n_months = n(),
    annual_total_mm = sum(value),
    mean_monthly_mm = mean(value),
    .groups = "drop"
  ) |>
  filter(n_months == 12)

wind_annual <- wind |>
  filter(quality_flag %in% numeric_flags, !is.na(value), year <= 2024) |>
  group_by(station_name, year) |>
  summarise(
    n_months = n(),
    annual_mean_ms = mean(value),
    .groups = "drop"
  ) |>
  filter(n_months == 12)

write_csv(rain_annual, file.path(tables, "r_rainfall_annual_by_station.csv"))
write_csv(wind_annual, file.path(tables, "r_wind_annual_by_station.csv"))

rain_network <- rain_annual |>
  group_by(year) |>
  summarise(
    n_stations = n(),
    mean_annual_mm = mean(annual_total_mm),
    sd_annual_mm = sd(annual_total_mm),
    min_annual_mm = min(annual_total_mm),
    max_annual_mm = max(annual_total_mm),
    .groups = "drop"
  )

wind_network <- wind_annual |>
  group_by(year) |>
  summarise(
    n_stations = n(),
    mean_annual_ms = mean(annual_mean_ms),
    sd_annual_ms = sd(annual_mean_ms),
    min_annual_ms = min(annual_mean_ms),
    max_annual_ms = max(annual_mean_ms),
    .groups = "drop"
  )

write_csv(rain_network, file.path(tables, "r_rainfall_network_annual.csv"))
write_csv(wind_network, file.path(tables, "r_wind_network_annual.csv"))

p_rain <- ggplot(rain_annual, aes(x = year, y = annual_total_mm)) +
  geom_point(colour = "grey55", alpha = 0.50, size = 1.4) +
  geom_line(data = rain_network, aes(y = mean_annual_mm),
            colour = "#08519c", linewidth = 1) +
  geom_point(data = rain_network, aes(y = mean_annual_mm),
             colour = "#08519c", size = 2.3) +
  scale_x_continuous(breaks = 2016:2024) +
  labs(
    title = "Annual rainfall totals by PAGASA station",
    subtitle = "Grey points are stations with 12 numeric months; blue is the unweighted network mean",
    x = "Year", y = "Annual rainfall (mm)",
    caption = "2025 is excluded. Station totals are not area-weighted and do not represent Laguna de Bay as a basin."
  )

ggsave(file.path(figures, "fig_rainfall_annual_totals.png"), p_rain,
       width = 10, height = 5.5, dpi = 150)

p_wind <- ggplot(wind_annual, aes(x = year, y = annual_mean_ms)) +
  geom_point(colour = "grey55", alpha = 0.50, size = 1.4) +
  geom_line(data = wind_network, aes(y = mean_annual_ms),
            colour = "#a63603", linewidth = 1) +
  geom_point(data = wind_network, aes(y = mean_annual_ms),
             colour = "#a63603", size = 2.3) +
  scale_x_continuous(breaks = 2016:2024) +
  labs(
    title = "Annual mean wind speed by PAGASA station",
    subtitle = "Grey points are stations with 12 numeric months; orange is the unweighted network mean",
    x = "Year", y = "Mean wind speed (m/s)",
    caption = "2025 is excluded. Monthly source values are summaries, not daily observations."
  )

ggsave(file.path(figures, "fig_wind_annual_mean.png"), p_wind,
       width = 10, height = 5.5, dpi = 150)

weather_trend_one <- function(data, value_col) {
  n <- nrow(data)
  if (n < 8 || sd(data[[value_col]]) == 0) {
    return(tibble(
      n_years = n,
      first_year = min(data$year),
      last_year = max(data$year),
      slope_per_year = NA_real_,
      slope_p_value = NA_real_,
      r_squared = NA_real_,
      kendall_tau = NA_real_,
      kendall_p_value = NA_real_
    ))
  }
  data$value <- data[[value_col]]
  fit <- lm(value ~ year, data = data)
  coefs <- summary(fit)$coefficients
  slope <- if ("year" %in% rownames(coefs)) coefs["year", "Estimate"] else NA_real_
  slope_p <- if ("year" %in% rownames(coefs)) coefs["year", "Pr(>|t|)"] else NA_real_
  kt <- suppressWarnings(cor.test(data$year, data$value, method = "kendall", exact = FALSE))
  tibble(
    n_years = n,
    first_year = min(data$year),
    last_year = max(data$year),
    slope_per_year = unname(slope),
    slope_p_value = unname(slope_p),
    r_squared = summary(fit)$r.squared,
    kendall_tau = unname(kt$estimate),
    kendall_p_value = kt$p.value
  )
}

rain_trends <- rain_annual |>
  group_by(station_name) |>
  group_modify(~ weather_trend_one(.x, "annual_total_mm")) |>
  ungroup() |>
  mutate(variable = "Rainfall annual total", unit = "mm/year")

wind_trends <- wind_annual |>
  group_by(station_name) |>
  group_modify(~ weather_trend_one(.x, "annual_mean_ms")) |>
  ungroup() |>
  mutate(variable = "Wind-speed annual mean", unit = "m/s per year")

weather_trends <- bind_rows(rain_trends, wind_trends) |>
  group_by(variable) |>
  mutate(slope_p_adj_bh = p.adjust(slope_p_value, method = "BH")) |>
  ungroup() |>
  arrange(variable, slope_p_value)

write_csv(weather_trends, file.path(tables, "r_weather_trend_tests.csv"))

# ---------------------------------------------------------------------------
# Human-readable summary
# ---------------------------------------------------------------------------

trend_counts <- station_trends |>
  filter(!is.na(slope_p_value)) |>
  group_by(variable) |>
  summarise(
    tested = n(),
    raw_p_lt_005 = sum(slope_p_value < 0.05),
    bh_q_lt_005 = sum(slope_p_adj_bh < 0.05),
    .groups = "drop"
  )

do_sig <- station_trends |>
  filter(variable == "Dissolved oxygen (DO)", slope_p_adj_bh < 0.05) |>
  arrange(slope_per_year) |>
  mutate(direction = ifelse(slope_per_year < 0, "decreasing", "increasing"))

lines <- c(
  "# R environmental-trend summary",
  "",
  "Generated by `r/environmental_trends.R` from annual station summaries.",
  "",
  "## Method",
  "",
  "- Station trend: ordinary least squares of value on year, for stations with at least five",
  "  numeric annual values; Kendall tau is also reported.",
  "- Multiple testing: Benjamini-Hochberg adjustment within each variable.",
  "- Network series: unweighted mean across reporting lake stations.",
  "- Weather trends use only station-years with 12 numeric months, 2016-2024.",
  "",
  "## Station-trend counts",
  "",
  "| Variable | Stations tested | Raw p < 0.05 | BH q < 0.05 |",
  "|---|---:|---:|---:|"
)

for (i in seq_len(nrow(trend_counts))) {
  lines <- c(
    lines,
    sprintf("| %s | %d | %d | %d |",
            trend_counts$variable[[i]], trend_counts$tested[[i]],
            trend_counts$raw_p_lt_005[[i]], trend_counts$bh_q_lt_005[[i]])
  )
}

lines <- c(
  lines,
  "",
  "## Dissolved oxygen",
  "",
  if (nrow(do_sig) == 0) {
    "No lake station had a Benjamini-Hochberg-adjusted DO trend below 0.05."
  } else {
    paste0(
      sprintf("%d station(s) had a BH-adjusted DO slope below 0.05: ", nrow(do_sig)),
      paste(sprintf("%s (%s, %.3f mg/L/year)", do_sig$station_name,
                    do_sig$direction, do_sig$slope_per_year), collapse = "; "),
      "."
    )
  },
  "",
  "## Weather",
  "",
  "- Annual rainfall and wind trends are exploratory. The PAGASA network is not a lagoon-wide",
  "  sample, station membership changes, and 2025 is excluded.",
  "",
  "## Limits",
  "",
  "- Ten annual points per lake station at most. Serial correlation, measurement changes and",
  "  unrecorded sampling design changes are not modelled.",
  "- Annual summaries hide within-year timing; a trend does not identify a fish-kill mechanism.",
  "- Raw and adjusted p-values describe the supplied data only, not a causal effect.",
  "- No fish-kill label was used; this is not a model-evaluation result.",
  "",
  "## Outputs",
  "",
  "- `r_water_quality_network_annual.csv`, `r_water_quality_station_trends.csv`",
  "- `r_rainfall_annual_by_station.csv`, `r_wind_annual_by_station.csv`",
  "- `r_rainfall_network_annual.csv`, `r_wind_network_annual.csv`",
  "- `r_weather_trend_tests.csv`",
  "- Figures prefixed `fig_network_` and `fig_*_annual` in `reports/figures/`"
)

writeLines(lines, file.path(tables, "r_trends_summary.md"), useBytes = TRUE)

message("R environmental trends complete")
message("Tables: ", tables)
message("Figures: ", figures)
