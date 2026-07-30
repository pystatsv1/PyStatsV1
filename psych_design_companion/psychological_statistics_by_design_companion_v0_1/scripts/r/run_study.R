args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 2) stop("usage: Rscript scripts/r/run_study.R ROOT STUDY_ID")
root <- normalizePath(args[[1]], mustWork = TRUE)
study_id <- toupper(gsub("_", "-", args[[2]]))
map <- list(
  "SWL-S01"=c("swl_s01_s06_s07_v0_1","swl_s01","run_swl_s01","SWL-S01.csv"),
  "SWL-S02"=c("swl_s02_s05_v0_1","swl_s02","run_swl_s02","SWL-S02_r_results.csv"),
  "SWL-S03"=c("swl_s02_s05_v0_1","swl_s03","run_swl_s03","SWL-S03_r_results.csv"),
  "SWL-S04"=c("swl_s02_s05_v0_1","swl_s04","run_swl_s04","SWL-S04_r_results.csv"),
  "SWL-S05"=c("swl_s02_s05_v0_1","swl_s05","run_swl_s05","SWL-S05_r_results.csv"),
  "SWL-S06"=c("swl_s01_s06_s07_v0_1","swl_s06","run_swl_s06","SWL-S06.csv"),
  "SWL-S07"=c("swl_s01_s06_s07_v0_1","swl_s07","run_swl_s07","SWL-S07.csv"),
  "SWL-S08"=c("swl_s08_s10_v0_1","swl_s08","run_swl_s08","SWL-S08.csv"),
  "SWL-S09"=c("swl_s08_s10_v0_1","swl_s09","run_swl_s09","SWL-S09.csv"),
  "SWL-S10"=c("swl_s08_s10_v0_1","swl_s10","run_swl_s10","SWL-S10.csv")
)
entry <- map[[study_id]]
if (is.null(entry)) stop(sprintf("unknown study ID: %s", study_id))
batch <- entry[[1]]; slug <- entry[[2]]; function_name <- entry[[3]]; raw_name <- entry[[4]]
base <- file.path(root,"scripts","r","batches",batch)
source(file.path(base,"common.R"), local=.GlobalEnv)
source(file.path(base,paste0(slug,".R")), local=.GlobalEnv)
out <- file.path(root,"outputs",tolower(gsub("-","_",study_id)))
dir.create(out,recursive=TRUE,showWarnings=FALSE)
do.call(function_name,list(root,out))
raw <- file.path(out,raw_name); final <- file.path(out,"r_result.csv")
if (!file.exists(raw)) stop(sprintf("R study did not write expected file: %s", raw))
if (file.exists(final)) file.remove(final)
if (!file.rename(raw,final)) stop("could not normalize R result filename")
cat(sprintf("PYSTATSV1_PSYCH_DESIGN_R_STUDY_OK study=%s result=%s\n",study_id,final))
