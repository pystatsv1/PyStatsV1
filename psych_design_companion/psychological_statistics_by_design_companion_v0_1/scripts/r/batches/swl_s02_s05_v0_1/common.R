validated_metric_values <- function(metrics) {
  metric_names <- names(metrics)
  values <- as.numeric(unlist(metrics, use.names = FALSE))
  if (length(values) != length(metric_names)) {
    stop("R metric names and values differ in length")
  }
  invalid <- !is.finite(values)
  if (any(invalid)) {
    stop(sprintf(
      "non-finite R metric(s): %s",
      paste(metric_names[invalid], collapse = ", ")
    ))
  }
  values
}

write_metrics <- function(path, metrics) {
  dir.create(dirname(path), recursive = TRUE, showWarnings = FALSE)
  frame <- data.frame(
    metric = names(metrics),
    value = validated_metric_values(metrics),
    stringsAsFactors = FALSE
  )
  frame <- frame[order(frame$metric), ]
  write.csv(frame, path, row.names = FALSE, quote = TRUE)
}

pooled_sd <- function(x, y) {
  sqrt(((length(x) - 1) * var(x) + (length(y) - 1) * var(y)) /
    (length(x) + length(y) - 2))
}
