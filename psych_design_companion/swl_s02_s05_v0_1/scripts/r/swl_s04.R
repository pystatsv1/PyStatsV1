run_swl_s04 <- function(root, output_root) {
  data <- read.csv(
    file.path(root, "data", "swl_s04_three_condition_support.csv"),
    stringsAsFactors = FALSE
  )
  levels_order <- c(
    "standard_support",
    "guided_practice",
    "guided_practice_plus_feedback"
  )
  data$support_condition <- factor(
    data$support_condition,
    levels = levels_order
  )
  if (any(is.na(data$support_condition))) {
    stop("SWL-S04 contains an unregistered support condition")
  }

  group_values <- lapply(
    levels_order,
    function(level) {
      data$assessment_performance[data$support_condition == level]
    }
  )
  names(group_values) <- levels_order
  group_counts <- vapply(group_values, length, numeric(1))
  group_means <- vapply(group_values, mean, numeric(1))
  if (any(group_counts == 0)) {
    stop("SWL-S04 requires every registered support condition")
  }

  grand_mean <- mean(data$assessment_performance)
  ss_between <- sum(group_counts * (group_means - grand_mean)^2)
  ss_within <- sum(vapply(
    levels_order,
    function(level) {
      sum((group_values[[level]] - group_means[[level]])^2)
    },
    numeric(1)
  ))
  df_between <- length(levels_order) - 1
  df_within <- nrow(data) - length(levels_order)
  ms_between <- ss_between / df_between
  mse <- ss_within / df_within
  anova_f <- ms_between / mse
  p_value <- pf(anova_f, df_between, df_within, lower.tail = FALSE)

  coefficients_1 <- c(-1.0, 0.5, 0.5)
  names(coefficients_1) <- levels_order
  estimate_1 <- sum(coefficients_1 * group_means)
  se_1 <- sqrt(mse * sum(coefficients_1^2 / group_counts))
  t_1 <- estimate_1 / se_1
  p_1 <- 2 * pt(abs(t_1), df = df_within, lower.tail = FALSE)

  coefficients_2 <- c(0.0, -1.0, 1.0)
  names(coefficients_2) <- levels_order
  estimate_2 <- sum(coefficients_2 * group_means)
  se_2 <- sqrt(mse * sum(coefficients_2^2 / group_counts))
  t_2 <- estimate_2 / se_2
  p_2 <- 2 * pt(abs(t_2), df = df_within, lower.tail = FALSE)
  adjusted <- p.adjust(c(p_1, p_2), method = "holm")

  metrics <- list(
    n_total = nrow(data),
    n_standard_support = group_counts[["standard_support"]],
    n_guided_practice = group_counts[["guided_practice"]],
    n_guided_practice_plus_feedback = group_counts[[
      "guided_practice_plus_feedback"
    ]],
    mean_standard_support = group_means[["standard_support"]],
    mean_guided_practice = group_means[["guided_practice"]],
    mean_guided_practice_plus_feedback = group_means[[
      "guided_practice_plus_feedback"
    ]],
    anova_f = anova_f,
    df_between = df_between,
    df_within = df_within,
    p_value = p_value,
    eta_squared = ss_between / (ss_between + ss_within),
    contrast_guided_average_minus_standard_estimate = estimate_1,
    contrast_guided_average_minus_standard_t = t_1,
    contrast_guided_average_minus_standard_p = p_1,
    contrast_guided_average_minus_standard_p_holm = adjusted[1],
    contrast_feedback_increment_estimate = estimate_2,
    contrast_feedback_increment_t = t_2,
    contrast_feedback_increment_p = p_2,
    contrast_feedback_increment_p_holm = adjusted[2]
  )
  write_metrics(file.path(output_root, "SWL-S04_r_results.csv"), metrics)
}
