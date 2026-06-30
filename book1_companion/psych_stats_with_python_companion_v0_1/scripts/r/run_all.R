#!/usr/bin/env Rscript
args <- commandArgs(trailingOnly = FALSE)
script_arg <- args[grep('^--file=', args)][1]
root <- normalizePath(file.path(dirname(sub('^--file=', '', script_arg)), '..', '..'), mustWork = TRUE)
source(file.path(root, "scripts", "r", "common.R"))

scripts <- c(
  "ch05_independent_t.R", "ch06_paired_t.R", "ch07_one_way_anova.R", "ch08_two_way_anova.R",
  "ch09_repeated_measures_anova.R", "ch10_correlation.R", "ch11_regression.R", "ch12_apa_reporting.R"
)
for (script in scripts) {
  status <- system2("Rscript", file.path(root, "scripts", "r", script))
  if (status != 0) stop(paste("failed:", script))
}
