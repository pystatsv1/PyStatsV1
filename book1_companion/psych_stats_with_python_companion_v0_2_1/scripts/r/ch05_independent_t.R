#!/usr/bin/env Rscript
args <- commandArgs(trailingOnly = FALSE)
script_arg <- args[grep('^--file=', args)][1]
root <- normalizePath(file.path(dirname(sub('^--file=', '', script_arg)), '..', '..'), mustWork = TRUE)
source(file.path(root, "scripts", "r", "common.R"))

d <- read.csv(file.path(root, "data", "ch05_independent.csv"))
structured <- subset(d, group == "structured")$test_score
standard <- subset(d, group == "standard")$test_score
test <- t.test(structured, standard, var.equal = FALSE)
n1 <- length(structured); n2 <- length(standard)
v1 <- var(structured); v2 <- var(standard)
pooled_sd <- sqrt(((n1 - 1) * v1 + (n2 - 1) * v2) / (n1 + n2 - 2))
write_result(root, "ch05", "Welch independent-samples t-test", "data/ch05_independent.csv", list(
  structured_mean = mean(structured), structured_sd = sd(structured),
  standard_mean = mean(standard), standard_sd = sd(standard),
  t_statistic = unname(test$statistic), degrees_of_freedom = unname(test$parameter),
  p_value = test$p.value, cohen_d = (mean(structured) - mean(standard)) / pooled_sd
))
