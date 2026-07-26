run_swl_s10 <- function(root, output_root) {
  data <- read.csv(
    file.path(root, "data", "swl_s10_replication_program.csv"),
    stringsAsFactors = FALSE,
    check.names = FALSE
  )
  d <- data$observed_cohens_d
  variance <- data$sampling_variance_d
  weights <- 1 / variance
  pooled <- sum(weights * d) / sum(weights)
  se <- sqrt(1 / sum(weights))
  z <- pooled / se
  p <- 2 * pnorm(-abs(z))
  ci_low <- pooled - 1.96 * se
  ci_high <- pooled + 1.96 * se
  q <- sum(weights * (d - pooled)^2)
  df_q <- length(d) - 1
  p_q <- pchisq(q, df = df_q, lower.tail = FALSE)
  i2 <- if (q > 0) max(0, (q - df_q) / q * 100) else 0
  n_for_power <- function(effect_size, power, alpha = 0.05) {
    z_alpha <- qnorm(1 - alpha / 2)
    z_power <- qnorm(power)
    2 * ((z_alpha + z_power) / effect_size)^2
  }
  n80 <- n_for_power(0.40, 0.80)
  n90 <- n_for_power(0.40, 0.90)
  metrics <- c(
    study_count = nrow(data),
    total_participants = sum(data$total_n),
    target_effect_size_d = 0.40,
    planning_alpha_two_sided = 0.05,
    planning_power_primary = 0.80,
    planning_n_per_group_unrounded_80 = n80,
    planning_n_per_group_ceiling_80 = ceiling(n80),
    planning_power_sensitivity = 0.90,
    planning_n_per_group_unrounded_90 = n90,
    planning_n_per_group_ceiling_90 = ceiling(n90),
    minimum_observed_d = min(d),
    maximum_observed_d = max(d),
    fixed_effect_pooled_d = pooled,
    fixed_effect_se = se,
    fixed_effect_z = z,
    fixed_effect_p = p,
    fixed_effect_ci_95_low = ci_low,
    fixed_effect_ci_95_high = ci_high,
    cochran_q = q,
    cochran_q_df = df_q,
    cochran_q_p = p_q,
    i_squared_percent = i2
  )
  write_metrics(file.path(output_root, "SWL-S10.csv"), metrics)
}
