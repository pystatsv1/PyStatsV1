run_swl_s07 <- function(root, output_root) {
  data <- read.csv(file.path(root, "data", "swl_s07_baseline_adjusted_intervention.csv"), stringsAsFactors = FALSE)
  data$treatment <- ifelse(data$intervention_group == "intervention", 1, 0)
  baseline_mean <- mean(data$baseline_performance)
  data$baseline_centered <- data$baseline_performance - baseline_mean
  model <- lm(post_performance ~ treatment + baseline_centered, data = data)
  summary_model <- summary(model)
  coefficients <- coef(summary_model)
  intervals <- confint(model, level = 0.95)
  interaction_model <- lm(post_performance ~ treatment * baseline_centered, data = data)
  interaction_summary <- summary(interaction_model)
  interaction_coefficients <- coef(interaction_summary)
  group_t <- coefficients["treatment", "t value"]
  group_f <- group_t^2
  df_error <- df.residual(model)
  adjusted_comparison <- coefficients["(Intercept)", "Estimate"]
  adjusted_difference <- coefficients["treatment", "Estimate"]
  comparison <- data$intervention_group == "comparison"
  intervention <- data$intervention_group == "intervention"
  metrics <- c(
    n_total = nrow(data),
    n_comparison = sum(comparison),
    n_intervention = sum(intervention),
    baseline_overall_mean = baseline_mean,
    raw_baseline_mean_comparison = mean(data$baseline_performance[comparison]),
    raw_baseline_mean_intervention = mean(data$baseline_performance[intervention]),
    raw_post_mean_comparison = mean(data$post_performance[comparison]),
    raw_post_mean_intervention = mean(data$post_performance[intervention]),
    adjusted_mean_comparison_at_overall_baseline = adjusted_comparison,
    adjusted_mean_intervention_at_overall_baseline = adjusted_comparison + adjusted_difference,
    adjusted_group_difference_intervention_minus_comparison = adjusted_difference,
    group_effect_se = coefficients["treatment", "Std. Error"],
    group_effect_t = group_t,
    group_effect_p = coefficients["treatment", "Pr(>|t|)"],
    group_effect_ci_95_low = intervals["treatment", 1],
    group_effect_ci_95_high = intervals["treatment", 2],
    group_effect_f = group_f,
    group_effect_df = 1,
    model_df_error = df_error,
    group_partial_eta_squared = group_f / (group_f + df_error),
    baseline_slope = coefficients["baseline_centered", "Estimate"],
    baseline_slope_se = coefficients["baseline_centered", "Std. Error"],
    baseline_slope_t = coefficients["baseline_centered", "t value"],
    baseline_slope_p = coefficients["baseline_centered", "Pr(>|t|)"],
    baseline_slope_ci_95_low = intervals["baseline_centered", 1],
    baseline_slope_ci_95_high = intervals["baseline_centered", 2],
    model_r_squared = summary_model$r.squared,
    model_adjusted_r_squared = summary_model$adj.r.squared,
    homogeneity_interaction_b = interaction_coefficients["treatment:baseline_centered", "Estimate"],
    homogeneity_interaction_se = interaction_coefficients["treatment:baseline_centered", "Std. Error"],
    homogeneity_interaction_t = interaction_coefficients["treatment:baseline_centered", "t value"],
    homogeneity_interaction_p = interaction_coefficients["treatment:baseline_centered", "Pr(>|t|)"]
  )
  write_metrics(file.path(output_root, "SWL-S07.csv"), metrics)
}
