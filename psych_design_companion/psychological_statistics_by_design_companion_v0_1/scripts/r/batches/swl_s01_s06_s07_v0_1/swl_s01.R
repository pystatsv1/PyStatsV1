run_swl_s01 <- function(root, output_root) {
  data <- read.csv(file.path(root, "data", "swl_s01_student_well_being_survey.csv"), stringsAsFactors = FALSE)
  if (nrow(data) != 120 || length(unique(data$participant_id)) != 120) stop("SWL-S01 row or ID count")
  correlation <- cor.test(data$sleep_quality, data$academic_confidence, method = "pearson")
  model <- lm(assessment_performance ~ study_hours_per_week + academic_confidence, data = data)
  model_summary <- summary(model)
  coefficients <- coef(model_summary)
  intervals <- confint(model, level = 0.95)
  fstat <- model_summary$fstatistic
  residual_df <- unname(fstat[[3]])
  mse <- sum(residuals(model)^2) / residual_df
  metrics <- c(
    n = nrow(data),
    correlation_r_sleep_confidence = unname(correlation$estimate),
    correlation_t = unname(correlation$statistic),
    correlation_df = unname(correlation$parameter),
    correlation_p_two_sided = correlation$p.value,
    correlation_ci_95_low = correlation$conf.int[[1]],
    correlation_ci_95_high = correlation$conf.int[[2]],
    regression_df_model = unname(fstat[[2]]),
    regression_df_residual = residual_df,
    regression_f = unname(fstat[[1]]),
    regression_p = pf(unname(fstat[[1]]), unname(fstat[[2]]), residual_df, lower.tail = FALSE),
    regression_r_squared = model_summary$r.squared,
    regression_adjusted_r_squared = model_summary$adj.r.squared,
    regression_rmse = sqrt(mse),
    intercept_b = coefficients["(Intercept)", "Estimate"],
    intercept_se = coefficients["(Intercept)", "Std. Error"],
    intercept_t = coefficients["(Intercept)", "t value"],
    intercept_p = coefficients["(Intercept)", "Pr(>|t|)"],
    intercept_ci_95_low = intervals["(Intercept)", 1],
    intercept_ci_95_high = intervals["(Intercept)", 2],
    study_hours_b = coefficients["study_hours_per_week", "Estimate"],
    study_hours_se = coefficients["study_hours_per_week", "Std. Error"],
    study_hours_t = coefficients["study_hours_per_week", "t value"],
    study_hours_p = coefficients["study_hours_per_week", "Pr(>|t|)"],
    study_hours_ci_95_low = intervals["study_hours_per_week", 1],
    study_hours_ci_95_high = intervals["study_hours_per_week", 2],
    confidence_b = coefficients["academic_confidence", "Estimate"],
    confidence_se = coefficients["academic_confidence", "Std. Error"],
    confidence_t = coefficients["academic_confidence", "t value"],
    confidence_p = coefficients["academic_confidence", "Pr(>|t|)"],
    confidence_ci_95_low = intervals["academic_confidence", 1],
    confidence_ci_95_high = intervals["academic_confidence", 2]
  )
  write_metrics(file.path(output_root, "SWL-S01.csv"), metrics)
}
