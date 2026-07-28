# Psychological Statistics by Design: SWL-S08–S10 Final Batch

This bounded PyStatsV1 source candidate implements the three remaining
study-specific asset sets required before Chapters 14 through 19 of
*Psychological Statistics by Design* may be constructed.

## Identity

- Baseline PyStatsV1 commit:
  `bb618a4c8c8186df43823b33bf2fab3e5d42330a`
- Book handoff commit:
  `2d8532a62e7b4f1ded957325426ac6ed16a69e06`
- Branch: `feat/psych-design-swl-s08-s10-final-batch`
- Candidate tag: `psych-design-swl-s08-s10-v0-1`
- Verification marker:
  `PYSTATSV1_PSYCH_DESIGN_SWL_S08_S10_VERIFY_OK`

This unit belongs in the PyStatsV1 repository. It does not modify the private
book manuscript. The book repository must explicitly accept the new merged and
tagged PyStatsV1 commit before controlled construction begins.

## Studies

### SWL-S08 — Longitudinal treatment and mixed models

Sixty synthetic participants are scheduled for baseline, post, and follow-up.
Twelve visits are omitted by a fixed identifier-based rule, leaving 168
observed rows. A maximum-likelihood random-intercept model estimates the
additional treatment-group changes at post and follow-up. Python uses
`statsmodels.MixedLM`; the independent R path uses `nlme::lme` with the same
rows, coding, fixed-effects formula, random structure, and likelihood target.
Fixed effects are compared under a declared V3 tolerance, while software-
specific inference remains an explicit V4 methodological comparison.

### SWL-S09 — Outcome and distribution extension

One balanced two-condition study registers two distinct outcomes:

- binary clinical-improvement status, analyzed with a chi-square independence
  test and Cramer's V;
- positive-skew recovery burden, analyzed with a two-sided Mann–Whitney test
  without continuity correction and a directional rank-biserial effect.

Separate result maps, figure specifications, and limitations prevent the two
analyses from being treated as interchangeable responses to a normality test.

### SWL-S10 — Power, replication, and cumulative evidence

A six-replication study-level dataset supports:

- prospective equal-allocation planning for a target standardized effect;
- a transparent fixed-effect synthesis with pooled effect, confidence interval,
  Cochran's Q, and I-squared.

The matched limitations state that power is conditional on planning
assumptions and that a fixed-effect synthesis does not address publication
bias, selective reporting, or meaningful heterogeneity.

## Verification

```bash
make psych-design-swl-s08-s10-verify
make psych-design-swl-s08-s10-r-verify
make psych-design-swl-s08-s10-figures
make lint
make test
```

The static target regenerates all governed datasets, contracts, results, APA
maps, figure specifications, limitations, and batch receipts in a copied
checkout and rejects byte-level drift. The R target runs three independent R
implementations and enforces exact V2 numeric parity for SWL-S09 and SWL-S10,
plus the declared V3 tolerances for SWL-S08.

R verification is now a governed local-only gate. GitHub-hosted workflows do
not install or execute R. Run the combined `make local-r-verify` gate in the
environment documented by `docs/LOCAL_R_VERIFICATION_POLICY.md`; the local
machine must provide the `nlme` R package.

## Exclusions

This source candidate does not:

- change the private book repository;
- advance the book's PyStatsV1 source anchor;
- authorize manuscript construction before a later book acceptance gate;
- publish a companion ZIP or portal download;
- change the PyPI version or publish to PyPI;
- authorize real participant or restricted data;
- authorize KDP production.
