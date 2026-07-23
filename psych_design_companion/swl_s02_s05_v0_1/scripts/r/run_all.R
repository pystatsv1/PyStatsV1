args <- commandArgs(trailingOnly = TRUE)
root <- if (length(args) >= 1) normalizePath(args[1]) else normalizePath(".")
output_root <- if (length(args) >= 2) {
  normalizePath(args[2], mustWork = FALSE)
} else {
  file.path(root, "outputs", "r")
}
script_root <- file.path(root, "scripts", "r")
source(file.path(script_root, "common.R"))
source(file.path(script_root, "swl_s02.R"))
source(file.path(script_root, "swl_s03.R"))
source(file.path(script_root, "swl_s04.R"))
source(file.path(script_root, "swl_s05.R"))
dir.create(output_root, recursive = TRUE, showWarnings = FALSE)
run_swl_s02(root, output_root)
run_swl_s03(root, output_root)
run_swl_s04(root, output_root)
run_swl_s05(root, output_root)
cat("PYSTATSV1_PSYCH_DESIGN_SWL_S02_S05_R_OUTPUTS_OK\n")
