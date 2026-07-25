args <- commandArgs(trailingOnly = TRUE)
root <- if (length(args) >= 1) normalizePath(args[1]) else normalizePath(".")
output_root <- if (length(args) >= 2) {
  normalizePath(args[2], mustWork = FALSE)
} else {
  file.path(root, "outputs", "r_verification")
}
script_root <- file.path(root, "scripts", "r")
source(file.path(script_root, "common.R"))
source(file.path(script_root, "swl_s01.R"))
source(file.path(script_root, "swl_s06.R"))
source(file.path(script_root, "swl_s07.R"))
dir.create(output_root, recursive = TRUE, showWarnings = FALSE)
run_swl_s01(root, output_root)
run_swl_s06(root, output_root)
run_swl_s07(root, output_root)
cat("PYSTATSV1_PSYCH_DESIGN_SWL_S01_S06_S07_R_OK\n")
