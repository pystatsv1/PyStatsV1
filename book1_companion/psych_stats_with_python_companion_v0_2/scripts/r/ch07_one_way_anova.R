#!/usr/bin/env Rscript
args <- commandArgs(trailingOnly = FALSE)
script_arg <- args[grep('^--file=', args)][1]
root <- normalizePath(file.path(dirname(sub('^--file=', '', script_arg)), '..', '..'), mustWork = TRUE)
source(file.path(root, "scripts", "r", "common.R"))

d <- read.csv(file.path(root, "data", "ch07_one_way_anova.csv"))
fit <- aov(test_score ~ study_condition, data = d)
tab <- summary(fit)[[1]]
ss_between <- tab["study_condition", "Sum Sq"]; ss_within <- tab["Residuals", "Sum Sq"]
means <- tapply(d$test_score, d$study_condition, mean)
write_result(root, "ch07", "One-way ANOVA", "data/ch07_one_way_anova.csv", list(
  practice_quiz_mean = means[["practice_quiz"]], retrieval_practice_mean = means[["retrieval_practice"]],
  spaced_review_mean = means[["spaced_review"]], f_statistic = tab["study_condition", "F value"],
  df_between = tab["study_condition", "Df"], df_within = tab["Residuals", "Df"],
  p_value = tab["study_condition", "Pr(>F)"], eta_squared = ss_between / (ss_between + ss_within)
))
