# Psychological Statistics by Design — SWL-S02 through SWL-S05

This is a source-candidate implementation batch for Chapters 6–9 of
*Psychological Statistics by Design*. It is synthetic-only and is not a public
companion release.

The batch contains four governed studies:

- SWL-S02: independent groups;
- SWL-S03: linked pre/post observations;
- SWL-S04: three groups with two registered planned contrasts;
- SWL-S05: a balanced strategy-by-feedback factorial experiment.

Python is the primary analysis path. Base R provides an independent numerical
verification path. Tracked data, contracts, receipts, figure specifications,
APA source maps, limitations, and exact-regeneration evidence are verified by
`make psych-design-swl-s02-s05-verify` from the repository root.

Run the complete local workflow from this directory with:

```bash
make all
```

Generated Python results, R results, parity receipts, and PNG figures are placed
under `outputs/` and are intentionally untracked. The book repository must not
update its PyStatsV1 source anchor until this batch is merged and the exact new
commit is known.
