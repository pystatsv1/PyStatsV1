# Psych Stats with Python — Executable Companion v0.2.1

This is the public, synthetic-only executable companion for *Psych Stats with
Python*. It is packaged by PyStatsV1 0.25.2 as an inspectable local folder.
The bundle keeps its analysis scripts visible: it does not upload data, choose
a study design, or turn a real-data workflow into a one-command claim.

It contains:

- versioned synthetic CSVs and transparent Python scripts;
- a machine-readable Chapter 5–11 design contract and deterministic audit;
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
pystatsv1 book1 verify --dest .
make design-audit
make figures
make all  # requires Rscript for Python/R parity
```

These commands answer different questions:

- `pystatsv1 book1 verify --dest .` checks source-file integrity against the
  packaged bundle manifest;
- `make design-audit` checks whether rows, identifiers, factor levels,
  repeated observations, variable pairings, analysis bindings, figure
  bindings, and reporting bindings match `BOOK1_DESIGN_CONTRACT.json`;
- `make figures` regenerates the six declared visual-evidence artifacts; and
- `make all` runs the synthetic Python/R calculation and parity workflow.

A passed source-integrity check does not by itself establish that the table
represents the intended design. A passed design audit does not establish
measurement validity, ethical authorization, assumption adequacy, causal
identification, practical importance, or generalizability.

`make design-audit` writes deterministic generated evidence to:

- `outputs/design/BOOK1_DESIGN_AUDIT_RECEIPT.json`; and
- `outputs/design/BOOK1_DESIGN_AUDIT_SUMMARY.md`.

The audit keeps semantic-design validity separate from the exact release
fingerprint. For example, a structurally valid modified teaching table can have
`semantic_design_status=PASS` and `release_fingerprint_status=FAIL` at the same
time. The statuses are intentionally not collapsed.

Maintainers can run the permanent temporary-copy mutation suite with:

```bash
make design-test
```

The tests do not alter the canonical synthetic CSVs.

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
