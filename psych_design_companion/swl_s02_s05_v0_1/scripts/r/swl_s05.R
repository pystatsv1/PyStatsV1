run_swl_s05 <- function(root, output_root) {
  data <- read.csv(
    file.path(root, "data", "swl_s05_strategy_feedback.csv"),
    stringsAsFactors = FALSE
  )
  strategies <- c("rereading", "retrieval_practice")
  feedback_levels <- c("no_feedback", "explanatory_feedback")
  data$study_strategy <- factor(
    data$study_strategy,
    levels = strategies
  )
  data$feedback_condition <- factor(
    data$feedback_condition,
    levels = feedback_levels
  )
  if (any(is.na(data$study_strategy)) || any(is.na(data$feedback_condition))) {
    stop("SWL-S05 contains an unregistered factor level")
  }

  cell_counts <- with(
    data,
    table(study_strategy, feedback_condition)
  )
  observed_cell_sizes <- unique(as.numeric(cell_counts))
  if (length(observed_cell_sizes) != 1 || observed_cell_sizes[1] <= 0) {
    stop("SWL-S05 requires balanced nonempty cell sizes")
  }
  n_per_cell <- observed_cell_sizes[1]

  cell_means <- with(
    data,
    tapply(
      assessment_performance,
      list(study_strategy, feedback_condition),
      mean
    )
  )
  strategy_means <- with(
    data,
    tapply(assessment_performance, study_strategy, mean)
  )
  feedback_means <- with(
    data,
    tapply(assessment_performance, feedback_condition, mean)
  )
  grand_mean <- mean(data$assessment_performance)

  ss_strategy <- length(feedback_levels) * n_per_cell * sum(
    (strategy_means - grand_mean)^2
  )
  ss_feedback <- length(strategies) * n_per_cell * sum(
    (feedback_means - grand_mean)^2
  )
  ss_interaction <- n_per_cell * sum(vapply(
    strategies,
    function(strategy) {
      sum(vapply(
        feedback_levels,
        function(feedback) {
          (
            cell_means[strategy, feedback] -
              strategy_means[[strategy]] -
              feedback_means[[feedback]] +
              grand_mean
          )^2
        },
        numeric(1)
      ))
    },
    numeric(1)
  ))

  fitted_cell_means <- mapply(
    function(strategy, feedback) {
      cell_means[strategy, feedback]
    },
    as.character(data$study_strategy),
    as.character(data$feedback_condition)
  )
  ss_within <- sum((data$assessment_performance - fitted_cell_means)^2)
  df_within <- nrow(data) - length(cell_means)
  mse <- ss_within / df_within

  strategy_f <- ss_strategy / mse
  feedback_f <- ss_feedback / mse
  interaction_f <- ss_interaction / mse
  strategy_p <- pf(strategy_f, 1, df_within, lower.tail = FALSE)
  feedback_p <- pf(feedback_f, 1, df_within, lower.tail = FALSE)
  interaction_p <- pf(interaction_f, 1, df_within, lower.tail = FALSE)

  se_simple <- sqrt(mse * (2 / n_per_cell))
  simple_no <- cell_means["retrieval_practice", "no_feedback"] -
    cell_means["rereading", "no_feedback"]
  simple_feedback <- cell_means[
    "retrieval_practice",
    "explanatory_feedback"
  ] - cell_means["rereading", "explanatory_feedback"]
  t_no <- simple_no / se_simple
  t_feedback <- simple_feedback / se_simple
  p_no <- 2 * pt(abs(t_no), df = df_within, lower.tail = FALSE)
  p_feedback <- 2 * pt(abs(t_feedback), df = df_within, lower.tail = FALSE)

  metrics <- list(
    n_total = nrow(data),
    n_per_cell = n_per_cell,
    mean_rereading_no_feedback = cell_means[
      "rereading",
      "no_feedback"
    ],
    mean_retrieval_no_feedback = cell_means[
      "retrieval_practice",
      "no_feedback"
    ],
    mean_rereading_explanatory_feedback = cell_means[
      "rereading",
      "explanatory_feedback"
    ],
    mean_retrieval_explanatory_feedback = cell_means[
      "retrieval_practice",
      "explanatory_feedback"
    ],
    strategy_f = strategy_f,
    strategy_p = strategy_p,
    strategy_partial_eta_squared = ss_strategy / (ss_strategy + ss_within),
    feedback_f = feedback_f,
    feedback_p = feedback_p,
    feedback_partial_eta_squared = ss_feedback / (ss_feedback + ss_within),
    interaction_f = interaction_f,
    interaction_p = interaction_p,
    interaction_partial_eta_squared = ss_interaction /
      (ss_interaction + ss_within),
    df_effect = 1,
    df_within = df_within,
    interaction_difference_in_differences = simple_feedback - simple_no,
    simple_strategy_no_feedback_estimate = simple_no,
    simple_strategy_no_feedback_t = t_no,
    simple_strategy_no_feedback_p = p_no,
    simple_strategy_explanatory_feedback_estimate = simple_feedback,
    simple_strategy_explanatory_feedback_t = t_feedback,
    simple_strategy_explanatory_feedback_p = p_feedback
  )
  write_metrics(file.path(output_root, "SWL-S05_r_results.csv"), metrics)
}
