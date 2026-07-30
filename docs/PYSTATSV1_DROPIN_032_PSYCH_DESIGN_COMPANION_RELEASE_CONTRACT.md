# PyStatsV1 Drop-in 032 - Psychological Statistics by Design Companion Release Contract and Unified Study Registry

## Baseline

- Repository: `PyStatsV1`
- Exact source-archive main: `6cd680812c7a149d4909eff4ddaf6e1679f6aba1`
- Package version: `0.25.2`
- Branch: `feat/psych-design-companion-release-contract`
- Intended tag: `psych-design-companion-release-contract-v0-1`

## Purpose

Freeze the smallest safe cross-repository contract before building or releasing
the advanced-book companion. The unit inventories all ten governed SWL studies,
proves that the three source-candidate batches remain byte-exact, selects SWL-S02
as the first-result route, freezes the planned `psych-design` command family,
and records every release blocker.

## Planned release identity (not public)

- PyStatsV1: `0.26.0`
- Extra: `psych-design`
- CLI namespace: `pystatsv1 psych-design`
- Companion: `Psychological Statistics by Design - Executable Companion v0.1`
- Destination: `psychological_statistics_by_design_companion_v0_1`
- Asset: `psychological_statistics_by_design_companion_v0_1.zip`

These are frozen implementation targets, not claims of an existing PyPI release,
portal page, or downloadable public asset.

## Exact scope

- `Makefile`
- `docs/PYSTATSV1_DROPIN_032_PSYCH_DESIGN_COMPANION_RELEASE_CONTRACT.md`
- `psych_design_companion/psych_design_release_contract_v0_1/*`
- `tools/check_psych_design_release_contract.py`
- `tests/test_psych_design_release_contract.py`

The existing three study-batch directories are not edited.

## Gates

```bash
make psych-design-release-contract-verify
python -m pytest -q tests/test_psych_design_release_contract.py
make lint
make test
```

The first two are focused gates for this unit. The complete repository lint and
test suite remain required before merge in the supported project environment.

## Completion marker

`PYSTATSV1_PSYCH_DESIGN_RELEASE_CONTRACT_VERIFY_OK`

## Explicit exclusions

This unit does not change `pyproject.toml`, package version, CLI wiring, packaged
assets, public release state, portal content, book source, study results, data,
Python/R calculations, or real-data authorization.
