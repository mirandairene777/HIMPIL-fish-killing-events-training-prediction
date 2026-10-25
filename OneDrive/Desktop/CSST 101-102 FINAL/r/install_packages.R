# HIMPIL - install the R packages used by the analysis scripts.
#
# Run from the project root:
#   "C:\Program Files\R\R-4.6.1\bin\Rscript.exe" r\install_packages.R
#
# The scripts use the standard user library. On this machine that is
# C:\Users\<name>\AppData\Local\R\win-library\4.6. If R asks whether to use a
# personal library, answer yes.

options(repos = c(CRAN = "https://cloud.r-project.org"))

required <- c(
  "readr",     # documented CSV exchange with Python
  "dplyr",     # summaries and grouped operations
  "tidyr",     # long/wide reshaping
  "ggplot2",   # research figures
  "scales"     # axis and number formatting
)

installed <- rownames(installed.packages())
missing <- setdiff(required, installed)

if (length(missing) == 0) {
  cat("All required R packages are already installed.\n")
} else {
  cat("Installing:", paste(missing, collapse = ", "), "\n")
  install.packages(missing, dependencies = TRUE)
}

cat("Library paths:\n")
cat(.libPaths(), sep = "\n")
cat("\nPackage check:\n")
for (package in required) {
  cat(sprintf("  %-12s %s\n", package, requireNamespace(package, quietly = TRUE)))
}
