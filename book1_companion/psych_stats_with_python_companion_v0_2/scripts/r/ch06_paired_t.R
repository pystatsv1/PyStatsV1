#!/usr/bin/env Rscript
args <- commandArgs(trailingOnly = FALSE)
script_arg <- args[grep('^--file=', args)][1]
root <- normalizePath(file.path(dirname(sub('^--file=', '', script_arg)), '..', '..'), mustWork = TRUE)
source(file.path(root, "scripts", "r", "common.R"))

d <- read.csv(file.path(root, "data", "ch06_paired.csv"))
diff <- d$anxiety_post - d$anxiety_pre
test <- t.test(d$anxiety_post, d$anxiety_pre, paired = TRUE)
write_result(root, "ch06", "Paired-samples t-test", "data/ch06_paired.csv", list(
  pre_mean = mean(d$anxiety_pre), post_mean = mean(d$anxiety_post),
  mean_difference_post_minus_pre = mean(diff), t_statistic = unname(test$statistic),
  degrees_of_freedom = unname(test$parameter), p_value = test$p.value,
  cohen_dz = mean(diff) / sd(diff)
))
