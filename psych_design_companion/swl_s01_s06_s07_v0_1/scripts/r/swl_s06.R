run_swl_s06 <- function(root, output_root) {
  data <- read.csv(file.path(root, "data", "swl_s06_confidence_trajectory.csv"), stringsAsFactors = FALSE, na.strings = c("", "NA"))
  occasions <- c("baseline", "post", "follow_up")
  wide <- reshape(data[, c("participant_id", "occasion", "academic_confidence")], idvar = "participant_id", timevar = "occasion", direction = "wide")
  columns <- paste0("academic_confidence.", occasions)
  wide <- wide[, c("participant_id", columns)]
  complete <- wide[complete.cases(wide[, columns]), columns]
  y <- as.matrix(complete)
  n <- nrow(y)
  k <- ncol(y)
  grand <- mean(y)
  subject_means <- rowMeans(y)
  occasion_means <- colMeans(y)
  ss_total <- sum((y - grand)^2)
  ss_subjects <- k * sum((subject_means - grand)^2)
  ss_within <- ss_total - ss_subjects
  ss_occasion <- n * sum((occasion_means - grand)^2)
  ss_error <- ss_within - ss_occasion
  df_occasion <- k - 1
  df_error <- (n - 1) * (k - 1)
  f_value <- (ss_occasion / df_occasion) / (ss_error / df_error)
  covariance <- cov(y)
  centering <- diag(k) - matrix(1 / k, nrow = k, ncol = k)
  transformed <- centering %*% covariance %*% centering
  tr <- sum(diag(transformed))
  epsilon <- tr^2 / ((k - 1) * sum(diag(transformed %*% transformed)))
  epsilon <- max(1 / (k - 1), min(1, epsilon))
  gg_df_occasion <- epsilon * df_occasion
  gg_df_error <- epsilon * df_error
  missing_counts <- colSums(is.na(wide[, columns]))
  metrics <- c(
    n_scheduled_participants = nrow(wide),
    scheduled_rows = nrow(wide) * k,
    observed_outcomes = sum(!is.na(wide[, columns])),
    missing_outcomes = sum(is.na(wide[, columns])),
    missing_baseline = missing_counts[[1]],
    missing_post = missing_counts[[2]],
    missing_follow_up = missing_counts[[3]],
    n_complete_case = n,
    n_incomplete_participants = nrow(wide) - n,
    mean_baseline_complete_case = occasion_means[[1]],
    mean_post_complete_case = occasion_means[[2]],
    mean_follow_up_complete_case = occasion_means[[3]],
    mean_change_post_minus_baseline = occasion_means[[2]] - occasion_means[[1]],
    mean_change_follow_up_minus_baseline = occasion_means[[3]] - occasion_means[[1]],
    rm_anova_f = f_value,
    rm_anova_df_occasion = df_occasion,
    rm_anova_df_error = df_error,
    rm_anova_p = pf(f_value, df_occasion, df_error, lower.tail = FALSE),
    greenhouse_geisser_epsilon = epsilon,
    greenhouse_geisser_df_occasion = gg_df_occasion,
    greenhouse_geisser_df_error = gg_df_error,
    greenhouse_geisser_p = pf(f_value, gg_df_occasion, gg_df_error, lower.tail = FALSE),
    partial_eta_squared = ss_occasion / (ss_occasion + ss_error)
  )
  write_metrics(file.path(output_root, "SWL-S06.csv"), metrics)
}
