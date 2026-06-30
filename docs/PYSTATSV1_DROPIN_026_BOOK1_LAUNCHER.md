# PyStatsV1 Drop-in 026 — Book 1 Launcher

## Purpose

This drop-in prepares PyStatsV1 v0.24.0 to provision an inspectable local copy
of the synthetic-only **Psych Stats with Python — Executable Companion v0.1**.

The public CLI surface is deliberately small:

```bash
pystatsv1 book1 info
pystatsv1 book1 init --dest psych_stats_with_python_companion_v0_1
pystatsv1 book1 verify --dest psych_stats_with_python_companion_v0_1
```

`book1 init` refuses to overwrite an existing destination. It checks archive
paths and the package manifest before it writes a local working copy.

## Source and package contract

- PyStatsV1 stores an explicit Book 1 source snapshot under
  `book1_companion/psych_stats_with_python_companion_v0_1/`.
- `tools/build_book1_companion_asset.py` deterministically builds the packaged
  asset at `src/pystatsv1/assets/psych_stats_with_python_companion_v0_1.zip`.
- The asset includes only synthetic teaching files and a manifest of every
  immutable source file. It excludes `outputs/`, cache directories, and
  compiled Python artifacts.
- `pystatsv1 book1 verify` validates the extracted source files. It deliberately
  does not validate generated analysis outputs; those require the explicit
  Python/R companion workflow.
- The copied companion requirements intentionally require PyStatsV1 v0.24.x,
  the release series that contains this launcher. This does not alter the
  historical LearnToProgram.ca v0.1 downloadable ZIP; a later portal release
  may align its published environment constraint after PyPI publication.

## Strict boundary

This drop-in does not upload to PyPI, change the Book 1 KDP proof, change
portal deployment, or claim that a local install authorizes real-data analysis.
It is a package-source and launcher layer only.

## Local proof

```bash
python -m pip install -e '.[dev]'
make book1-asset
python -m pytest -q tests/test_book1_launcher.py
python -m build --wheel
```

The CI wheel-smoke job runs `pystatsv1 book1 init` and `pystatsv1 book1 verify`
on Ubuntu, macOS, and Windows.
