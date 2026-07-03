#!/usr/bin/env Rscript
args <- commandArgs(trailingOnly = FALSE)
script_arg <- args[grep('^--file=', args)][1]
root <- normalizePath(file.path(dirname(sub('^--file=', '', script_arg)), '..', '..'), mustWork = TRUE)
source(file.path(root, "scripts", "r", "common.R"))

d <- read.csv(file.path(root, "data", "ch11_regression.csv"))
fit <- lm(test_score ~ study_hours, data = d)
s <- summary(fit)
coefs <- s$coefficients
write_result(root, "ch11", "Simple linear regression", "data/ch11_regression.csv", list(
  intercept = coefs["(Intercept)", "Estimate"], slope = coefs["study_hours", "Estimate"],
  slope_standard_error = coefs["study_hours", "Std. Error"], t_statistic = coefs["study_hours", "t value"],
  degrees_of_freedom = s$df[2], p_value = coefs["study_hours", "Pr(>|t|)"], r_squared = s$r.squared, n = nrow(d)
))
