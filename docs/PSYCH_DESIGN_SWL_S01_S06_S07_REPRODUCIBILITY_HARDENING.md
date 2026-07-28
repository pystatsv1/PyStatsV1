# Psych Design SWL-S01/S06/S07 Reproducibility Hardening

This maintenance unit closes the environment-governance gap identified during the KDP factual audit of *Psychological Statistics by Design*.

## Changes

- The dedicated workflow uses Python 3.10 and installs the batch-specific pinned requirements.
- PyStatsV1 is installed with `--no-deps`, preventing the package's broad runtime ranges from replacing the governed numerical stack.
- `ENVIRONMENT_CONTRACT.json` and an executable environment checker assert the exact NumPy, pandas, and SciPy versions used for receipt identity.
- The companion checker distinguishes structural validation from exact numerical identity.
- Exact mismatches report the specific fields and absolute numerical differences.
- General mutation tests use structural mode so a baseline library drift cannot hide the intended contract failure.

## Boundaries

No dataset, analysis formula, reported field, APA binding, figure specification, result receipt, R parity field, public-release state, or book result changes. The historical analysis baseline remains `da9abc9d5c71779cf794804cce6cfe245980b988`.
