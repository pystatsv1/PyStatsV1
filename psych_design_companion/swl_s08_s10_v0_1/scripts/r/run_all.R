#!/usr/bin/env Rscript

args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 2) {
  stop("Usage: run_all.R COMPANION_ROOT OUTPUT_ROOT")
}
root <- normalizePath(args[[1]], mustWork = TRUE)
output_root <- args[[2]]
if (!dir.exists(output_root)) {
  dir.create(output_root, recursive = TRUE)
}
source(file.path(root, "scripts", "r", "common.R"))
source(file.path(root, "scripts", "r", "swl_s08.R"))
source(file.path(root, "scripts", "r", "swl_s09.R"))
source(file.path(root, "scripts", "r", "swl_s10.R"))
run_swl_s08(root, output_root)
run_swl_s09(root, output_root)
run_swl_s10(root, output_root)
cat("PYSTATSV1_PSYCH_DESIGN_SWL_S08_S10_R_OUTPUTS_OK\n")
