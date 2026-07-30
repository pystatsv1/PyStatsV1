run_swl_s02 <- function(root, output_root) {
  data <- read.csv(
    file.path(root, "data", "swl_s02_structured_study_routine.csv"),
    stringsAsFactors = FALSE
  )
  standard <- data$post_session_performance[
    data$study_routine_group == "standard_routine"
  ]
  structured <- data$post_session_performance[
    data$study_routine_group == "structured_routine"
  ]
  test <- t.test(structured, standard, var.equal = FALSE, conf.level = 0.95)
  difference <- mean(structured) - mean(standard)
  metrics <- list(
    n_standard = length(standard),
    n_structured = length(structured),
    mean_standard = mean(standard),
    mean_structured = mean(structured),
    sd_standard = sd(standard),
    sd_structured = sd(structured),
    mean_difference_structured_minus_standard = difference,
    welch_t = unname(test$statistic),
    welch_df = unname(test$parameter),
    p_value_two_sided = test$p.value,
    ci_95_low = test$conf.int[1],
    ci_95_high = test$conf.int[2],
    cohen_d_pooled = difference / pooled_sd(structured, standard)
  )
  write_metrics(file.path(output_root, "SWL-S02_r_results.csv"), metrics)
}
