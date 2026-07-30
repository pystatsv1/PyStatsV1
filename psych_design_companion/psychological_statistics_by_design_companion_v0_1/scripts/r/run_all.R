args <- commandArgs(trailingOnly=TRUE)
if (length(args)!=1) stop("usage: Rscript scripts/r/run_all.R ROOT")
root <- normalizePath(args[[1]],mustWork=TRUE)
for (i in 1:10) {
  study <- sprintf("SWL-S%02d",i)
  status <- system2("Rscript",c(file.path(root,"scripts/r/run_study.R"),root,study))
  if (status!=0) stop(sprintf("R study failed: %s",study))
}
cat("PYSTATSV1_PSYCH_DESIGN_ALL_R_OK\n")
