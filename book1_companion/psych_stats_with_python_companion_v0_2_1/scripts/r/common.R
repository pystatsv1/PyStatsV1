json_escape <- function(value) {
  value <- gsub("\\\\", "\\\\\\\\", as.character(value))
  value <- gsub('"', '\\\\"', value, fixed = TRUE)
  value
}

json_number <- function(value) {
  sprintf("%.10g", as.numeric(value))
}

write_result <- function(root, chapter, analysis_name, data_file, fields) {
  out_dir <- file.path(root, "outputs", chapter)
  dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)
  field_lines <- vapply(names(fields), function(name) {
    sprintf('    "%s": %s', name, json_number(fields[[name]]))
  }, character(1))
  json <- paste0(
    '{\n',
    '  "schema_version": "book1-companion-results-v0.2",\n',
    sprintf('  "chapter": "%s",\n', chapter),
    sprintf('  "analysis_name": "%s",\n', json_escape(analysis_name)),
    '  "engine": "base-r",\n',
    sprintf('  "data_file": "%s",\n', data_file),
    '  "synthetic_data_only": true,\n',
    '  "reported_fields": {\n',
    paste(field_lines, collapse = ',\n'), '\n',
    '  }\n',
    '}\n'
  )
  writeLines(json, file.path(out_dir, "r_results.json"), useBytes = TRUE)
}

script_root <- function() {
  args <- commandArgs(trailingOnly = FALSE)
  candidate <- args[grep('^--file=', args)]
  if (length(candidate) == 0) stop('Rscript --file path was not found')
  normalizePath(file.path(dirname(sub('^--file=', '', candidate[[1]])), '..', '..'), mustWork = TRUE)
}
