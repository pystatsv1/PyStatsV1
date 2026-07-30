run_swl_s03 <- function(root, output_root) {
  data <- read.csv(
    file.path(root, "data", "swl_s03_skills_workshop_pre_post.csv"),
    stringsAsFactors = FALSE
  )
  pre <- data[data$occasion == "pre", c("participant_id", "academic_confidence")]
  post <- data[data$occasion == "post", c("participant_id", "academic_confidence")]
  names(pre)[2] <- "pre"
  names(post)[2] <- "post"
  paired <- merge(pre, post, by = "participant_id", all = FALSE, sort = TRUE)
  change <- paired$post - paired$pre
  test <- t.test(paired$post, paired$pre, paired = TRUE, conf.level = 0.95)
  metrics <- list(
    n_paired = nrow(paired),
    mean_pre = mean(paired$pre),
    mean_post = mean(paired$post),
    mean_change_post_minus_pre = mean(change),
    sd_change = sd(change),
    paired_t = unname(test$statistic),
    df = unname(test$parameter),
    p_value_two_sided = test$p.value,
    ci_95_low = test$conf.int[1],
    ci_95_high = test$conf.int[2],
    cohen_dz = mean(change) / sd(change)
  )
  write_metrics(file.path(output_root, "SWL-S03_r_results.csv"), metrics)
}
