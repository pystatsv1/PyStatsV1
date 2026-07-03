# Drop-in 030.1 — Public Companion Figure Workflow Repair

## Purpose

Drop-in 030 correctly packaged the public Book 1 Companion v0.2 asset, but a
legacy candidate-only status guard remained in the copied figure generator.
The public `figures_specs.json` declares `release_status: public_release`, so
`make figures` incorrectly stopped before it generated the six released
grayscale evidence figures.

This release-blocker repair is applied on top of PyStatsV1 0.25.0 source
commit `7027e4e4121ad1cff4db6b16f630d8dd93efc55b`, before the `v0.25.0` tag or
PyPI publication. It does not change the PyStatsV1 version, the Companion v0.2
data, Python/R statistical calculations, figure specifications, portal
handoff, or historical v0.24.1/v0.4 artifacts.

## Repair contract

- The public generator requires exactly `release_status: public_release`.
- Missing, candidate-only, and unknown statuses fail before any figure is
  written.
- The generated `outputs/figure_manifest.json` records `public_release`.
- A regression test extracts the packaged asset through the Book 1 launcher
  and runs the figure generator from that extracted public route.
- Wheel smoke exercises `make figures` on Linux and macOS; Windows invokes the
  same generator directly from the wheel-extracted folder.
- A new Ubuntu release-smoke job installs base R and runs both `make figures`
  and `make all` with `set -euo pipefail`, so a failed figures step cannot be
  masked by a later parity-only command.

## Release boundary

Do not tag `v0.25.0` or publish PyStatsV1 to PyPI until this repair is merged,
CI is green, and the fail-fast fresh-wheel proof completes locally. The final
publication proof must use a fresh PyPI installation after the trusted
publisher release succeeds.
