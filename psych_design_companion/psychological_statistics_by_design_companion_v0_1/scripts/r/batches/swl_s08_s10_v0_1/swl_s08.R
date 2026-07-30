run_swl_s08 <- function(root, output_root) {
  if (!requireNamespace("nlme", quietly = TRUE)) {
    stop("The recommended R package 'nlme' is required for SWL-S08 verification.")
  }
  data <- read.csv(
    file.path(root, "data", "swl_s08_longitudinal_treatment.csv"),
    stringsAsFactors = FALSE,
    check.names = FALSE
  )
  if (anyDuplicated(data[c("participant_id", "occasion")]) != 0) {
    stop("Duplicate SWL-S08 participant/occasion keys detected.")
  }
  fit <- nlme::lme(
    fixed = well_being_score ~ treatment + post + followup + treatment_post + treatment_followup,
    random = ~ 1 | participant_id,
    data = data,
    method = "ML",
    na.action = na.fail,
    control = nlme::lmeControl(
      maxIter = 200,
      msMaxIter = 200,
      niterEM = 50,
      returnObject = TRUE
    )
  )
  coef_table <- summary(fit)$tTable
  visits <- table(data$participant_id)
  mean_at <- function(group, occasion) {
    mean(data$well_being_score[
      data$treatment_group == group & data$occasion == occasion
    ])
  }
  metrics <- c(
    n_participants = length(unique(data$participant_id)),
    n_control = length(unique(data$participant_id[data$treatment_group == "control"])),
    n_treatment = length(unique(data$participant_id[data$treatment_group == "treatment"])),
    scheduled_rows = 180,
    observed_rows = nrow(data),
    missing_visits = 180 - nrow(data),
    complete_participants = sum(visits == 3),
    incomplete_participants = sum(visits == 2),
    control_baseline_mean = mean_at("control", "baseline"),
    control_post_mean = mean_at("control", "post"),
    control_followup_mean = mean_at("control", "followup"),
    treatment_baseline_mean = mean_at("treatment", "baseline"),
    treatment_post_mean = mean_at("treatment", "post"),
    treatment_followup_mean = mean_at("treatment", "followup"),
    intercept_b = coef_table["(Intercept)", "Value"],
    intercept_se = coef_table["(Intercept)", "Std.Error"],
    treatment_b = coef_table["treatment", "Value"],
    treatment_se = coef_table["treatment", "Std.Error"],
    post_b = coef_table["post", "Value"],
    post_se = coef_table["post", "Std.Error"],
    followup_b = coef_table["followup", "Value"],
    followup_se = coef_table["followup", "Std.Error"],
    treatment_post_b = coef_table["treatment_post", "Value"],
    treatment_post_se = coef_table["treatment_post", "Std.Error"],
    treatment_followup_b = coef_table["treatment_followup", "Value"],
    treatment_followup_se = coef_table["treatment_followup", "Std.Error"]
  )
  write_metrics(file.path(output_root, "SWL-S08.csv"), metrics)
}
