# Psychological Statistics by Design: SWL-S02–S05 First Batch

This bounded PyStatsV1 source-candidate implements the four synthetic studies
required before Chapters 6–9 of *Psychological Statistics by Design* may be
drafted.

## Identity

- Baseline PyStatsV1 commit:
  `621b1eb4a534f4dfedb0647b7e0853a7fd9b8a90`
- Book handoff commit:
  `0bb3db0c53dd3bb7ad18adc682a3fe1d39de5df0`
- Branch: `feat/psych-design-swl-s02-s05-first-batch`
- Candidate tag: `psych-design-swl-s02-s05-v0-1`
- Verification marker: `PYSTATSV1_PSYCH_DESIGN_SWL_S02_S05_VERIFY_OK`

This work does not change the PyPI package version and does not authorize a
public companion release. The book repository must record the exact new merged
PyStatsV1 commit before changing its source anchor.

## Studies

- **SWL-S02:** two independent groups with a declared assignment procedure;
- **SWL-S03:** linked pre/post observations with explicit post-minus-pre change;
- **SWL-S04:** three independent conditions and two registered planned contrasts;
- **SWL-S05:** a balanced two-by-two strategy-by-feedback experiment whose
  interaction is the primary question.

Every study includes a versioned synthetic CSV, a machine-readable design
contract, transparent Python analysis, an independent base-R script, a stable
result receipt, a grayscale figure specification, an APA number-source map, and
a matched limitation. The batch also includes an exact-regeneration receipt.

## Verification

```bash
make psych-design-swl-s02-s05-verify
make psych-design-swl-s02-s05-r-verify
make lint
make test
```

The first target regenerates every governed data and evidence artifact in a
temporary directory and rejects any byte-level drift. Mutation-oriented tests
reject duplicate identifiers, broken pairing, unregistered condition levels,
empty factorial cells, stale results, stale APA bindings, missing R paths, and
source-boundary changes.

The R target runs the four analyses independently with base R and compares all
reported numeric fields against the Python results within a declared tolerance.
Generated R outputs, parity receipts, and figures remain under ignored output
paths.

## Exclusions

This source-candidate does not:

- modify the private book manuscript;
- update the book's PyStatsV1 source anchor;
- publish a companion ZIP;
- modify the portal;
- accept real participant data;
- change the PyPI version or publish to PyPI.

### Base-R compatibility

The one-way and factorial verification scripts compute registered sums of
squares, mean squares, F statistics, and tail probabilities explicitly with
base R. This avoids version-sensitive ANOVA-table label lookup. The shared R
writer rejects any missing, infinite, or nonnumeric registered metric before a
parity CSV can be accepted.
