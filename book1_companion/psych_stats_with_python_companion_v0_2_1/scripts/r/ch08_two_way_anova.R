#!/usr/bin/env Rscript
args <- commandArgs(trailingOnly = FALSE)
script_arg <- args[grep('^--file=', args)][1]
root <- normalizePath(file.path(dirname(sub('^--file=', '', script_arg)), '..', '..'), mustWork = TRUE)
source(file.path(root, "scripts", "r", "common.R"))

d <- read.csv(file.path(root, "data", "ch08_two_way_anova.csv"))
fit <- aov(test_score ~ strategy * feedback, data = d)
tab <- anova(fit)
error_ss <- tab["Residuals", "Sum Sq"]
means <- with(d, tapply(test_score, list(strategy, feedback), mean))
write_result(root, "ch08", "Two-way factorial ANOVA", "data/ch08_two_way_anova.csv", list(
  standard_no_feedback_mean = means["standard", "no_feedback"], standard_feedback_mean = means["standard", "feedback"],
  structured_no_feedback_mean = means["structured", "no_feedback"], structured_feedback_mean = means["structured", "feedback"],
  strategy_f = tab["strategy", "F value"], strategy_p = tab["strategy", "Pr(>F)"],
  strategy_partial_eta_squared = tab["strategy", "Sum Sq"] / (tab["strategy", "Sum Sq"] + error_ss),
  feedback_f = tab["feedback", "F value"], feedback_p = tab["feedback", "Pr(>F)"],
  feedback_partial_eta_squared = tab["feedback", "Sum Sq"] / (tab["feedback", "Sum Sq"] + error_ss),
  interaction_f = tab["strategy:feedback", "F value"], interaction_p = tab["strategy:feedback", "Pr(>F)"],
  interaction_partial_eta_squared = tab["strategy:feedback", "Sum Sq"] / (tab["strategy:feedback", "Sum Sq"] + error_ss),
  df_effect = tab["strategy", "Df"], df_error = tab["Residuals", "Df"]
))
