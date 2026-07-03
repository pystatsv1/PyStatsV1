#!/usr/bin/env Rscript
args <- commandArgs(trailingOnly = FALSE)
script_arg <- args[grep('^--file=', args)][1]
root <- normalizePath(file.path(dirname(sub('^--file=', '', script_arg)), '..', '..'), mustWork = TRUE)
source(file.path(root, "scripts", "r", "common.R"))

d <- read.csv(file.path(root, "data", "ch09_repeated_measures.csv"))
wide <- xtabs(confidence_score ~ participant_id + time, data = d)[, c("baseline", "week_2", "week_4")]
n <- nrow(wide); k <- ncol(wide); grand <- mean(wide)
subject_means <- rowMeans(wide); time_means <- colMeans(wide)
ss_total <- sum((wide - grand)^2)
ss_subjects <- k * sum((subject_means - grand)^2)
ss_time <- n * sum((time_means - grand)^2)
ss_error <- ss_total - ss_subjects - ss_time
df_time <- k - 1; df_error <- (n - 1) * (k - 1)
f_value <- (ss_time / df_time) / (ss_error / df_error)
write_result(root, "ch09", "One-factor repeated-measures ANOVA", "data/ch09_repeated_measures.csv", list(
  baseline_mean = time_means[["baseline"]], week_2_mean = time_means[["week_2"]], week_4_mean = time_means[["week_4"]],
  f_statistic = f_value, df_time = df_time, df_error = df_error,
  p_value = pf(f_value, df_time, df_error, lower.tail = FALSE), partial_eta_squared = ss_time / (ss_time + ss_error)
))
