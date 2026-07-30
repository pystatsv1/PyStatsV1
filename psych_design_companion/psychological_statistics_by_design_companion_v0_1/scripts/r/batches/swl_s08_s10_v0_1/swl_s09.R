run_swl_s09 <- function(root, output_root) {
  data <- read.csv(
    file.path(root, "data", "swl_s09_outcome_distribution_extension.csv"),
    stringsAsFactors = FALSE,
    check.names = FALSE
  )
  data$support_condition <- factor(
    data$support_condition,
    levels = c("comparison", "intervention")
  )
  data$clinically_improved <- factor(
    data$clinically_improved,
    levels = c("no", "yes")
  )
  observed <- table(data$support_condition, data$clinically_improved)
  chi <- suppressWarnings(chisq.test(observed, correct = FALSE))
  comparison <- data$recovery_burden_days[data$support_condition == "comparison"]
  intervention <- data$recovery_burden_days[data$support_condition == "intervention"]
  combined <- c(intervention, comparison)
  ranks <- rank(combined, ties.method = "average")
  n1 <- length(intervention)
  n2 <- length(comparison)
  u1 <- sum(ranks[seq_len(n1)]) - n1 * (n1 + 1) / 2
  tie_counts <- as.numeric(table(combined))
  tie_sum <- sum(tie_counts^3 - tie_counts)
  n <- n1 + n2
  variance <- n1 * n2 / 12 * ((n + 1) - tie_sum / (n * (n - 1)))
  expected_u <- n1 * n2 / 2
  z <- (u1 - expected_u) / sqrt(variance)
  p_rank <- 2 * pnorm(-abs(z))
  rank_biserial_lower <- 1 - 2 * u1 / (n1 * n2)
  metrics <- c(
    n_total = nrow(data),
    n_comparison = length(comparison),
    n_intervention = length(intervention),
    comparison_improved = observed["comparison", "yes"],
    comparison_not_improved = observed["comparison", "no"],
    intervention_improved = observed["intervention", "yes"],
    intervention_not_improved = observed["intervention", "no"],
    comparison_improved_proportion = observed["comparison", "yes"] / length(comparison),
    intervention_improved_proportion = observed["intervention", "yes"] / length(intervention),
    improved_risk_difference_intervention_minus_comparison =
      observed["intervention", "yes"] / length(intervention) -
      observed["comparison", "yes"] / length(comparison),
    chi_square = unname(chi$statistic),
    chi_square_df = unname(chi$parameter),
    chi_square_p = chi$p.value,
    cramers_v = sqrt(unname(chi$statistic) / nrow(data)),
    minimum_expected_cell_count = min(chi$expected),
    comparison_burden_median = median(comparison),
    intervention_burden_median = median(intervention),
    burden_median_difference_intervention_minus_comparison =
      median(intervention) - median(comparison),
    mann_whitney_u_intervention = u1,
    mann_whitney_z_no_continuity = z,
    mann_whitney_p_two_sided = p_rank,
    rank_biserial_intervention_lower = rank_biserial_lower,
    comparison_burden_min = min(comparison),
    comparison_burden_max = max(comparison),
    intervention_burden_min = min(intervention),
    intervention_burden_max = max(intervention)
  )
  write_metrics(file.path(output_root, "SWL-S09.csv"), metrics)
}
