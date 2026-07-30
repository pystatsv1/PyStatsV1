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
  write.table(
    frame,
    path,
    sep = ",",
    row.names = FALSE,
    col.names = TRUE,
    quote = TRUE,
    eol = "\n"
  )
}
