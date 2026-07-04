# PyStatsV1 Drop-in 031 — v0.25.1 Power Stability and Release Guard

## Purpose

This maintenance drop-in repairs the Chapter 20 independent-samples t-test
power helper under newer SciPy numerical paths and adds a release guard before
any PyPI trusted-publisher action.

## Baseline

* Repository: `~/projects/PyStatsV1`
* Expected starting commit: `f379a3bdc7315b203a82c80d09945eef5b3e8698`
* Expected starting package version: `0.25.0`

## Changes

* Calculates two-sided power with stable noncentral-t survival-function tails.
* Makes unsupported target power requests fail explicitly when `n_max` is too
  small.
* Adds regression coverage for the known `d = 0.50`, 80% power result
  (`n = 64` per group), large-sample finiteness, effect-direction symmetry, and
  unreachable search bounds.
* Adds a Python 3.10 CI matrix for the declared SciPy floor path and the current
  resolver path.
* Adds `make release-verify` and makes the manual PyPI workflow require an
  annotated `v<pyproject-version>` tag checked out at `HEAD`.

## Preserved boundaries

This drop-in does **not** alter the public Book 1 Companion v0.2 source, asset,
manifest, figures, synthetic data, calculations, or the canonical
`pystatsv1[book1]==0.25.0` proof binding. It does not publish to PyPI, modify a
Git tag, or change the LearnToProgram portal.

## Required validation

Run:

```bash
make test-psych-ch20-problems
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q
make lint
python -m build
```

After committing and pushing the maintenance source, create the annotated
`v0.25.1` tag only after the main-branch CI is green. Then run
`make release-verify` locally from that tag and wait for tag CI before manually
dispatching the existing trusted-publisher workflow.
