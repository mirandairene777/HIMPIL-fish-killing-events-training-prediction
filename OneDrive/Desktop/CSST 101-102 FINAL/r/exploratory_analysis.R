# HIMPIL Phase 7a - exploratory analysis in R
#
# Reads the documented CSV interface produced by Python, not the Excel
# workbooks. It describes distributions, coverage and missingness. It does not
# create labels or model results.
#
# Run from anywhere:
#   "C:\Program Files\R\R-4.6.1\bin\Rscript.exe" r/exploratory_analysis.R

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
month_levels <- c("Jan", "Feb", "Mar", "Apr", "May", "Jun",
                  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")

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

wq_long <- read_csv(
  file.path(processed, "water_quality_long.csv"),
  show_col_types = FALSE
)
lake <- read_csv(
  file.path(processed, "water_quality_lake_annual.csv"),
  show_col_types = FALSE
) |>
  rename(
    nitrate = Nitrate,
    phosphate = Phosphate,
    bod = BOD,
    ph = pH,
    water_temperature = `Water temperature`,
    do = `Dissolved oxygen (DO)`
  )

rain <- read_csv(
  file.path(processed, "rainfall_monthly.csv"),
  show_col_types = FALSE
)
wind <- read_csv(
  file.path(processed, "wind_monthly.csv"),
  show_col_types = FALSE
)

lake_numeric <- wq_long |>
  filter(station_type == "lake", quality_flag %in% numeric_flags, !is.na(value))

# ---------------------------------------------------------------------------
# Summary tables
# ---------------------------------------------------------------------------

summary_by_variable <- lake_numeric |>
  group_by(variable, unit) |>
  summarise(
    n_station_years = n(),
    n_stations = n_distinct(station_name),
    mean = mean(value),
    sd = sd(value),
    median = median(value),
    minimum = min(value),
    maximum = max(value),
    .groups = "drop"
  ) |>
  mutate(across(c(mean, sd, median, minimum, maximum), \(x) round(x, 4)))

summary_by_year <- lake_numeric |>
  group_by(year, variable, unit) |>
  summarise(
    n_stations = n(),
    mean = mean(value),
    sd = sd(value),
    median = median(value),
    minimum = min(value),
    maximum = max(value),
    .groups = "drop"
  ) |>
  mutate(across(c(mean, sd, median, minimum, maximum), \(x) round(x, 4)))

missing_by_year <- wq_long |>
  filter(station_type == "lake") |>
  group_by(year, variable) |>
  summarise(
    station_years_expected = n(),
    reported = sum(quality_flag %in% numeric_flags),
    missing = sum(!quality_flag %in% numeric_flags),
    missing_percent = round(100 * missing / station_years_expected, 2),
    .groups = "drop"
  )

station_coverage <- lake |>
  select(station_name, reported_lake_zone, year, nitrate, phosphate, bod, ph,
         water_temperature, do, variables_reported, all_six_reported) |>
  pivot_longer(
    cols = c(nitrate, phosphate, bod, ph, water_temperature, do),
    names_to = "variable",
    values_to = "value"
  ) |>
  group_by(station_name, reported_lake_zone) |>
  summarise(
    first_numeric_year = ifelse(all(is.na(value)), NA_integer_, min(year[!is.na(value)])),
    last_numeric_year = ifelse(all(is.na(value)), NA_integer_, max(year[!is.na(value)])),
    numeric_station_years = n_distinct(year[!is.na(value)]),
    complete_six_station_years = sum(!is.na(value)) / 6,
    .groups = "drop"
  ) |>
  mutate(complete_six_station_years = round(complete_six_station_years, 0))

do_by_zone_year <- lake_numeric |>
  filter(variable == "Dissolved oxygen (DO)", reported_lake_zone != "") |>
  group_by(reported_lake_zone, year) |>
  summarise(
    n_stations = n(),
    mean_do = mean(value),
    sd_do = sd(value),
    min_do = min(value),
    max_do = max(value),
    .groups = "drop"
  ) |>
  mutate(across(c(mean_do, sd_do, min_do, max_do), \(x) round(x, 4)))

write_csv(summary_by_variable, file.path(tables, "r_lake_summary_by_variable.csv"))
write_csv(summary_by_year, file.path(tables, "r_lake_summary_by_year.csv"))
write_csv(missing_by_year, file.path(tables, "r_missingness_by_year.csv"))
write_csv(station_coverage, file.path(tables, "r_station_coverage.csv"))
write_csv(do_by_zone_year, file.path(tables, "r_do_by_zone_year.csv"))

# ---------------------------------------------------------------------------
# Figures
# ---------------------------------------------------------------------------

completeness <- wq_long |>
  filter(station_type == "lake") |>
  group_by(station_name, year) |>
  summarise(
    reported = sum(quality_flag %in% numeric_flags),
    .groups = "drop"
  )

station_order <- completeness |>
  group_by(station_name) |>
  summarise(first_year = min(year[reported > 0]), .groups = "drop") |>
  arrange(first_year, station_name) |>
  pull(station_name)

completeness <- completeness |>
  mutate(
    station_name = factor(station_name, levels = station_order),
    year = factor(year)
  )

p_complete <- ggplot(completeness, aes(x = year, y = station_name, fill = reported)) +
  geom_tile(colour = "white", linewidth = 0.6) +
  geom_text(aes(label = reported), size = 3) +
  scale_fill_gradient2(
    low = "#b2182b", mid = "#f7f7f7", high = "#2166ac",
    midpoint = 3, limits = c(0, 6), breaks = 0:6,
    name = "Variables reported\n(of 6)"
  ) +
  labs(
    title = "Lake station-year completeness",
    subtitle = "Count of six annual water-quality variables with a numeric value",
    x = "Year", y = NULL,
    caption = "Annual station summaries. Missing cells are not zero; see water_quality_long.csv for flags."
  ) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1))

ggsave(file.path(figures, "fig_water_quality_completeness.png"), p_complete,
       width = 10, height = 6.5, dpi = 150)

p_do_box <- wq_long |>
  filter(station_type == "lake", variable == "Dissolved oxygen (DO)",
         quality_flag %in% numeric_flags, !is.na(value)) |>
  ggplot(aes(x = factor(year), y = value)) +
  geom_boxplot(fill = "#9ecae1", colour = "#08519c", outlier.size = 1.5) +
  geom_hline(yintercept = 5.0, linetype = "dashed", colour = "#b2182b") +
  annotate("text", x = 1.2, y = 5.12, label = "5.0 mg/L reference cited in the 2019 article",
           hjust = 0, size = 3, colour = "#b2182b") +
  labs(
    title = "Dissolved oxygen across lake stations, 2016-2025",
    subtitle = "Distribution of annual station values",
    x = "Year", y = "Dissolved oxygen (mg/L)",
    caption = "The 5.0 mg/L line is a reference cited in the 2019 UPD article, not a lake-wide legal finding. Annual values may be means or other summaries."
  ) +
  coord_cartesian(ylim = c(4.5, 10))

ggsave(file.path(figures, "fig_do_by_year.png"), p_do_box,
       width = 9, height = 5.5, dpi = 150)

do_tile <- wq_long |>
  filter(station_type == "lake", variable == "Dissolved oxygen (DO)") |>
  mutate(
    station_name = factor(station_name, levels = rev(station_order)),
    year = factor(year)
  )

p_do_tile <- ggplot(do_tile, aes(x = year, y = station_name, fill = value)) +
  geom_tile(colour = "white", linewidth = 0.6) +
  scale_fill_viridis_c(option = "C", direction = -1, na.value = "grey88",
                       name = "DO\n(mg/L)") +
  labs(
    title = "Dissolved oxygen by lake station and year",
    subtitle = "Grey tiles are missing, not zero",
    x = "Year", y = NULL
  ) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1))

ggsave(file.path(figures, "fig_do_station_year_heatmap.png"), p_do_tile,
       width = 10, height = 6.5, dpi = 150)

p_nutrients <- wq_long |>
  filter(station_type == "lake",
         variable %in% c("Nitrate", "Phosphate", "BOD"),
         quality_flag %in% numeric_flags, !is.na(value)) |>
  ggplot(aes(x = factor(year), y = value)) +
  geom_boxplot(fill = "#c7e9c0", colour = "#238b45", outlier.size = 1.3) +
  facet_wrap(~ variable, scales = "free_y", nrow = 1) +
  labs(
    title = "Nutrient and BOD annual station values",
    subtitle = "Each box is the distribution across lake stations in that year",
    x = "Year", y = "mg/L",
    caption = "Annual station summaries; sampling dates and the source aggregation rule are unavailable."
  ) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1))

ggsave(file.path(figures, "fig_nutrients_by_year.png"), p_nutrients,
       width = 12, height = 5, dpi = 150)

p_temp <- wq_long |>
  filter(station_type == "lake",
         variable %in% c("Water temperature", "pH"),
         quality_flag %in% numeric_flags, !is.na(value)) |>
  ggplot(aes(x = factor(year), y = value)) +
  geom_boxplot(fill = "#fdd0a2", colour = "#d94801", outlier.size = 1.3) +
  facet_wrap(~ variable, scales = "free_y", nrow = 1) +
  labs(
    title = "Water temperature and pH across lake stations",
    subtitle = "Annual station values, 2016-2025",
    x = "Year", y = "Value (deg C or pH units)"
  ) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1))

ggsave(file.path(figures, "fig_temperature_ph_by_year.png"), p_temp,
       width = 11, height = 5, dpi = 150)

rain_clean <- rain |>
  filter(quality_flag %in% numeric_flags, !is.na(value), year <= 2024) |>
  mutate(month = factor(month, levels = month_levels))

rain_clim <- rain_clean |>
  group_by(month_number, month) |>
  summarise(
    n_station_months = n(),
    mean_mm = mean(value),
    sd_mm = sd(value),
    median_mm = median(value),
    .groups = "drop"
  )

write_csv(rain_clim, file.path(tables, "r_rainfall_monthly_climatology.csv"))

p_rain <- ggplot(rain_clim, aes(x = month, y = mean_mm, group = 1)) +
  geom_ribbon(aes(ymin = pmax(mean_mm - sd_mm, 0), ymax = mean_mm + sd_mm),
              fill = "#6baed6", alpha = 0.25) +
  geom_line(colour = "#08519c", linewidth = 0.9) +
  geom_point(colour = "#08519c", size = 2) +
  scale_y_continuous(labels = number_format(accuracy = 1)) +
  labs(
    title = "Rainfall seasonality across PAGASA stations",
    subtitle = "Mean monthly total with +/- 1 SD across stations, 2016-2024",
    x = NULL, y = "Rainfall (mm per month)",
    caption = "2025 is excluded (partial and still undergoing verification). This is station variability, not a confidence interval."
  )

ggsave(file.path(figures, "fig_rainfall_climatology.png"), p_rain,
       width = 9, height = 5.2, dpi = 150)

rain_heat <- rain_clean |>
  group_by(year, month_number, month) |>
  summarise(mean_mm = mean(value), n_stations = n(), .groups = "drop") |>
  mutate(year = factor(year))

p_rain_heat <- ggplot(rain_heat, aes(x = month, y = year, fill = mean_mm)) +
  geom_tile(colour = "white", linewidth = 0.4) +
  scale_fill_viridis_c(option = "B", direction = 1, name = "Mean mm") +
  labs(
    title = "Monthly rainfall by year (network mean)",
    subtitle = "PAGASA stations with a numeric value in each month",
    x = NULL, y = NULL,
    caption = "2025 is excluded. A tile is the mean across reporting stations, not a basin areal average."
  )

ggsave(file.path(figures, "fig_rainfall_year_month.png"), p_rain_heat,
       width = 10, height = 5.5, dpi = 150)

wind_clean <- wind |>
  filter(quality_flag %in% numeric_flags, !is.na(value), year <= 2024) |>
  mutate(month = factor(month, levels = month_levels))

wind_clim <- wind_clean |>
  group_by(month_number, month) |>
  summarise(
    n_station_months = n(),
    mean_ms = mean(value),
    sd_ms = sd(value),
    median_ms = median(value),
    .groups = "drop"
  )

write_csv(wind_clim, file.path(tables, "r_wind_monthly_climatology.csv"))

p_wind <- ggplot(wind_clim, aes(x = month, y = mean_ms, group = 1)) +
  geom_ribbon(aes(ymin = pmax(mean_ms - sd_ms, 0), ymax = mean_ms + sd_ms),
              fill = "#fdae6b", alpha = 0.25) +
  geom_line(colour = "#a63603", linewidth = 0.9) +
  geom_point(colour = "#a63603", size = 2) +
  labs(
    title = "Wind-speed seasonality across PAGASA stations",
    subtitle = "Mean monthly value with +/- 1 SD across stations, 2016-2024",
    x = NULL, y = "Wind speed (m/s)",
    caption = "2025 is excluded (partial and still undergoing verification). Source values are monthly summaries, not daily observations."
  )

ggsave(file.path(figures, "fig_wind_climatology.png"), p_wind,
       width = 9, height = 5.2, dpi = 150)

# ---------------------------------------------------------------------------
# Short human-readable summary
# ---------------------------------------------------------------------------

n_stations <- n_distinct(lake$station_name)
n_station_years <- nrow(lake)
n_complete <- sum(lake$all_six_reported == "yes")
do_values <- lake_numeric |> filter(variable == "Dissolved oxygen (DO)")
rain_values <- rain |> filter(quality_flag %in% numeric_flags, !is.na(value))
wind_values <- wind |> filter(quality_flag %in% numeric_flags, !is.na(value))

summary_lines <- c(
  "# R exploratory analysis summary",
  "",
  "Generated by `r/exploratory_analysis.R` from the Python-cleaned CSV interface.",
  "",
  "## Coverage",
  "",
  sprintf("- Lake stations: **%d**", n_stations),
  sprintf("- Lake station-years: **%d**", n_station_years),
  sprintf("- Complete across six variables: **%d**", n_complete),
  sprintf("- Numeric DO station-years: **%d**", nrow(do_values)),
  sprintf("- Numeric rainfall station-months: **%d** (all years, including provisional 2025)", nrow(rain_values)),
  sprintf("- Numeric wind station-months: **%d** (all years, including provisional 2025)", nrow(wind_values)),
  "",
  "## Descriptive observations",
  "",
  sprintf("- DO ranges from %.2f to %.2f mg/L across numeric annual station values.",
          min(do_values$value), max(do_values$value)),
  sprintf("- The station-year median DO is %.2f mg/L.", median(do_values$value)),
  "- Rainfall is strongly seasonal, but the stations are a national PAGASA network, not a",
  "  probability sample of Laguna de Bay.",
  "- Water-temperature values are missing for every long-running lake station in 2017.",
  "",
  "## Limits",
  "",
  "- These are annual station summaries. No observation date exists in the cleaned water-quality",
  "  file, so no seasonal or event-window inference is possible.",
  "- Boxplots describe variation across stations and years, not a time series of daily conditions.",
  "- No fish-kill label, model, prediction or performance metric is produced here.",
  "",
  "## Outputs",
  "",
  "- `r_lake_summary_by_variable.csv`, `r_lake_summary_by_year.csv`",
  "- `r_missingness_by_year.csv`, `r_station_coverage.csv`, `r_do_by_zone_year.csv`",
  "- `r_rainfall_monthly_climatology.csv`, `r_wind_monthly_climatology.csv`",
  "- Figures prefixed `fig_` in `reports/figures/`"
)

writeLines(summary_lines, file.path(tables, "r_eda_summary.md"), useBytes = TRUE)

message("R exploratory analysis complete")
message("Tables: ", tables)
message("Figures: ", figures)
