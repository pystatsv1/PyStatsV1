# PyStatsV1 Drop-in B — v0.23.0 Release Prep

## Purpose

Prepare the public PyStatsV1 package for a reader-installable release that
contains the APA Lab psychology support helpers.

## Changes

- Bumped package version from `0.22.4` to `0.23.0`.
- Added release notes for `pystatsv1.psych`.
- Expanded documentation for:
  - `package_identity()`
  - `describe_by_group()`
  - `write_json_receipt()`
  - `compare_numeric_results()`
- Added a release-prep note at `docs/release/v0.23.0.md`.
- Updated CI so `v*` release tags run the full CI workflow.
- Changed PyPI publishing to a manual trusted-publisher workflow, so publication
  happens only after the release tag is green.
- Added release metadata tests.

## Expected verification

```bash
python -m pip install -e '.[dev,docs]'
make lint
make test
make docs-workbook-strict
python -m build
```

## Expected marker

```text
PYSTATSV1_DROPIN_B_V0_23_RELEASE_PREP_APPLIED_OK
```
