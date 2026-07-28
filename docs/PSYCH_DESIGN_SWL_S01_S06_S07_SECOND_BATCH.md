# Psychological Statistics by Design: SWL-S01/S06/S07 Second Batch

This bounded PyStatsV1 source candidate implements the three study-specific
asset sets required before Chapters 10 through 13 of *Psychological Statistics
by Design* may be drafted.

## Identity

- Baseline PyStatsV1 commit:
  `da9abc9d5c71779cf794804cce6cfe245980b988`
- Book handoff commit:
  `954835653734a33f234308fec78282b5dc8feb3d`
- Branch: `feat/psych-design-swl-s01-s06-s07-second-batch`
- Candidate tag: `psych-design-swl-s01-s06-s07-v0-1`
- Verification marker:
  `PYSTATSV1_PSYCH_DESIGN_SWL_S01_S06_S07_VERIFY_OK`

This unit belongs in the PyStatsV1 repository. It does not modify the private
book manuscript. After a green merge, the book repository must explicitly
accept the new PyStatsV1 commit before controlled drafting begins.

## Studies

### SWL-S01 - Student Well-Being Survey

One versioned synthetic survey supports two deliberately distinct questions:

- Chapter 11: Pearson association between sleep quality and academic
  confidence, with a Fisher-transformed confidence interval and explicit
  noncausal boundary;
- Chapter 12: multiple regression predicting assessment performance from
  weekly study hours and academic confidence, with residual, leverage,
  Cook's-distance, and observed-domain diagnostics.

Separate APA source maps, figure specifications, and matched limitations keep
association and prediction from being treated as the same claim.

### SWL-S06 - Confidence Trajectory Study

Sixty synthetic students have three scheduled occasions. Six scheduled
outcomes are missing, leaving 54 complete trajectories. The registered
repeated-measures ANOVA is explicitly complete-case and reports:

- scheduled and observed rows;
- missing visits by occasion;
- complete and incomplete participant counts;
- uncorrected and Greenhouse-Geisser-adjusted inferential fields;
- a limitation stating that complete-case analysis can be biased and does not
  replace the later mixed-model workflow.

### SWL-S07 - Baseline-Adjusted Intervention

A two-group synthetic intervention study estimates the adjusted post-score
difference at the overall baseline mean. The stable receipt includes:

- raw and adjusted means;
- the adjusted group coefficient, interval, F statistic, and partial eta
  squared;
- the baseline slope;
- an explicit group-by-baseline homogeneity-of-slopes diagnostic.

The matched limitation states that adjustment does not create randomization or
repair unmeasured confounding.

## Verification

```bash
make psych-design-swl-s01-s06-s07-verify
make psych-design-swl-s01-s06-s07-r-verify
make psych-design-swl-s01-s06-s07-figures
make lint
make test
```

The static target regenerates every governed dataset, design contract, result
receipt, APA source map, figure specification, limitation, and batch receipt in
a copied checkout and rejects byte-level drift. Mutation tests reject duplicate
identifiers, changed missing-visit counts, unbalanced ANCOVA groups, stale
results, stale APA pointers, missing R paths, source-anchor drift, and accidental
public-release claims.

The R target runs independent base-R implementations and compares the named
scientific fields against Python within the declared tolerance. Runtime R
outputs, parity receipts, and figures remain ignored build products.

## Exclusions

This source candidate does not:

- change the private book repository;
- advance the book's PyStatsV1 source anchor;
- authorize manuscript drafting before a later book acceptance gate;
- publish a companion ZIP or portal download;
- change the PyPI version or publish to PyPI;
- accept real participant, student, clinical, institutional, or restricted
  data;
- authorize KDP production.

## Reproducibility hardening

The dedicated Ubuntu workflow installs PyStatsV1 and all declared runtime dependencies while applying the batch-specific requirements file as a pip constraint. This preserves the exact governed NumPy, pandas, SciPy, and Matplotlib versions without leaving required PyStatsV1 dependencies absent. The workflow then verifies Python 3.10 and the exact package versions recorded in `ENVIRONMENT_CONTRACT.json` before exact receipt identity and independent R parity are evaluated.

The general repository test suite uses structural validation for this batch so that an unrelated numerical-library drift cannot mask tests of schema, provenance, APA binding, or lifecycle failures. Exact floating-point identity remains mandatory in the governed workflow, where a mismatch now identifies every differing field and its absolute difference.
