# Psychological Statistics by Design — Executable Companion v0.1

This is the **PyStatsV1 0.26.0 release candidate**, not a public release. It contains ten governed synthetic studies and no real participant data.

## First complete proof chain

```bash
python -m pip install -r requirements-psych-design-companion.txt
make first-result
```

The command runs SWL-S02 through source and layout checks, visible Python analysis, independent R analysis, V2 comparison, figure generation, APA source binding, matched limitation, and reviewer-packet construction.

## Visible routes

```bash
make list-studies
make design-audit
make study STUDY=SWL-S02
make verify-study STUDY=SWL-S02
make packet STUDY=SWL-S02
make all-python
make all-r
make parity
make figures
make reviewer-packets
make all
```

Python is the primary workflow. R is an independent verification path. PyStatsV1 initializes and verifies the source bundle; it does not choose a method, validate an instrument, authorize data, establish causality, or repair a confused design.

Reviewer packets include a bounded study-index record, source-manifest record, design and measurement contracts, data-layout audit, Python and R results, verification receipt, figure specifications and manifest, APA source map, and matched limitation. Every packet member is hash-recorded in `MANIFEST.json`.

Generated evidence is written under `outputs/` and is intentionally excluded from the immutable source manifest. `pystatsv1 psych-design verify --dest .` verifies the distributed source even after outputs have been generated.

## Adaptation boundary

`templates/` contains blank planning records. They are not a “replace the CSV” recipe. Adapting an authorized project requires a new study map, measurement map, data-layout contract, analysis plan, verification contract, source map, matched limitation, and delta ledger. Stop when authorization, privacy, construct definition, unit, clustering, missingness, model selection, multiplicity, or causal scope is unresolved.
