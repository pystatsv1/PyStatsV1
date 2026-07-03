# Psych Stats with Python — Executable Companion v0.2

This is the public, synthetic-only executable companion for *Psych Stats with
Python*. It is packaged by PyStatsV1 0.25.0 as an inspectable local folder.
The bundle keeps its analysis scripts visible: it does not upload data, choose
a study design, or turn a real-data workflow into a one-command claim.

It contains:

- versioned synthetic CSVs and transparent Python scripts;
- optional base-R verification scripts and parity receipts;
- six source-faithful figures for the five visual teaching placements;
- high-contrast grayscale marks for a black-and-white paperback;
- a declared 300-PPI minimum at the documented Book 1 image slot; and
- source hashes, captions, accessibility text, and evidence limits.

**Python for the workflow. R for verification. PyStatsV1 for the bridge.**

## Quick start

After extracting this folder with the PyStatsV1 launcher:

```bash
python -m pip install -r requirements-book1-companion.txt
make figures
make all  # requires Rscript for Python/R parity
pystatsv1 book1 verify --dest .
```

`make figures` writes `outputs/figures/` and
`outputs/figure_manifest.json`. They are generated evidence, not hand-edited
source files. `make all` runs the synthetic Python/R parity workflow and
requires `Rscript`.

## Figure evidence boundary

Chapter 10 and Chapter 11 use separate source-faithful figures:

- `fig_10_1_correlation_scatter` uses `data/ch10_correlation.csv`;
- `fig_11_1_regression_scatter` uses `data/ch11_regression.csv`.

The figure manifest records each image's source CSV, analysis script, Python
result path, APA source ID where applicable, SHA-256, captions, accessibility
text, and print-resolution evidence.

## Synthetic-data boundary

The bundle contains synthetic teaching data only. Do not put identifiable
participant data, credentials, restricted exports, or real coursework/thesis/lab
files into a public repository, public support folder, or public AI tool. This
is a teaching workflow, not a real-data analysis service.
