#!/usr/bin/env Rscript
args <- commandArgs(trailingOnly = FALSE)
script_arg <- args[grep('^--file=', args)][1]
root <- normalizePath(file.path(dirname(sub('^--file=', '', script_arg)), '..', '..'), mustWork = TRUE)
source(file.path(root, "scripts", "r", "common.R"))

chapters <- c("ch05", "ch06", "ch07", "ch08", "ch09", "ch10", "ch11")
missing <- sum(!file.exists(file.path(root, "outputs", chapters, "r_results.json")))
write_result(root, "ch12", "APA reporting source-map audit", "outputs/ch12/apa_reporting_source_map.json", list(
  source_record_count = length(chapters), required_python_result_files = length(chapters) - missing
))
