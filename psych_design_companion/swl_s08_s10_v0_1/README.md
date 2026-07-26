# SWL-S08 through SWL-S10 final source candidate

This private, synthetic-only PyStatsV1 batch supplies the remaining
study-specific assets required before Chapters 14 through 19 of
*Psychological Statistics by Design* may be constructed.

- **SWL-S08:** an unequal-visit longitudinal treatment study analyzed with a
  maximum-likelihood random-intercept model and independently checked with
  `nlme::lme` under a V3/V4 comparison policy;
- **SWL-S09:** one two-group study with a registered binary outcome and a
  separate positive-skew continuous outcome, supporting chi-square and
  Mann-Whitney analyses without treating either as a generic normality repair;
- **SWL-S10:** a six-replication study-level program supporting prospective
  power planning and a transparent fixed-effect cumulative-evidence analysis.

The batch is not a public companion release, does not change the PyPI package
version, does not authorize real data, and does not modify the private book
repository.

```bash
make psych-design-swl-s08-s10-verify
make psych-design-swl-s08-s10-r-verify
make psych-design-swl-s08-s10-figures
```
