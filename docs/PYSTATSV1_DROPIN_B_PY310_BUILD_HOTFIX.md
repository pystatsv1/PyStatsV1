# PyStatsV1 Drop-in B Python 3.10 and Build Hotfix

This hotfix repairs two release-prep verification issues found after applying PyStatsV1 Drop-in B.

## Fixes

- `tests/test_release_023_metadata.py` now supports Python 3.10 by falling back from `tomllib` to `tomli`.
- The contributor `dev` extra now installs `tomli` on Python versions earlier than 3.11.
- The contributor `dev` extra now installs `build`, so `python -m build` works after `python -m pip install -e '.[dev,docs]'`.

## Expected verification

```bash
python -m pip install -e '.[dev,docs]'
make lint
make test
make docs-workbook-strict
python -m build
```

Expected hotfix marker from the apply script:

```text
PYSTATSV1_DROPIN_B_PY310_BUILD_HOTFIX_APPLIED_OK
```
