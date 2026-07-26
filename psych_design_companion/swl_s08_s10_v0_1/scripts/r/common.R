write_metrics <- function(path, metrics) {
  if (is.null(names(metrics)) || any(names(metrics) == "")) {
    stop("All metrics must be named.")
  }
  numeric_metrics <- as.numeric(metrics)
  if (any(!is.finite(numeric_metrics))) {
    stop("All metrics must be finite numeric values.")
  }
  output_dir <- dirname(path)
  if (!dir.exists(output_dir)) {
    dir.create(output_dir, recursive = TRUE)
  }
  frame <- data.frame(
    metric = names(metrics),
    value = format(numeric_metrics, digits = 17, scientific = TRUE, trim = TRUE),
    stringsAsFactors = FALSE
  )
  write.csv(frame, path, row.names = FALSE, quote = FALSE)
}
