#!/usr/bin/env Rscript
args <- commandArgs(trailingOnly = FALSE)
script_arg <- args[grep('^--file=', args)][1]
root <- normalizePath(file.path(dirname(sub('^--file=', '', script_arg)), '..', '..'), mustWork = TRUE)
source(file.path(root, "scripts", "r", "common.R"))

d <- read.csv(file.path(root, "data", "ch10_correlation.csv"))
test <- cor.test(d$study_hours, d$test_score, method = "pearson")
write_result(root, "ch10", "Pearson correlation", "data/ch10_correlation.csv", list(
  study_hours_mean = mean(d$study_hours), test_score_mean = mean(d$test_score),
  correlation_r = unname(test$estimate), degrees_of_freedom = unname(test$parameter),
  p_value = test$p.value, n = nrow(d)
))
