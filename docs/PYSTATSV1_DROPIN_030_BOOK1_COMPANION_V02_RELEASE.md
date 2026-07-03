# Drop-in 030 — Public Book 1 Companion v0.2 Launcher Release

## Scope

This PyStatsV1 release layer packages the portal handoff tagged
`book1-companion-v0.2-candidate` at portal commit
`20076607ebf37245f0eb9ed7c5a56f56a042a8f5`.

It updates the default `pystatsv1 book1` asset to **Companion v0.2** and
PyStatsV1 **0.25.0**. The public bundle has six source-faithful,
high-contrast grayscale figures. It retains the synthetic CSVs and transparent
Python/R analysis scripts from the portal handoff.

The release does not modify the portal repository, alter the frozen Book 1
v0.4 proof candidate, generate a Book 1 v0.5 proof, or perform a PyPI publish
automatically.

## Release identity

* Package version: `0.25.0`
* Companion version: `v0.2`
* Default extracted folder: `psych_stats_with_python_companion_v0_2`
* Portal source tag: `book1-companion-v0.2-candidate`
* Portal source commit: `20076607ebf37245f0eb9ed7c5a56f56a042a8f5`
* Preserved historical portal proof tag: `book1-kdp-proof-candidate-v0.4`

## Evidence boundary

The package checks the unchanged data/script hashes recorded in
`BOOK1_PORTAL_HANDOFF_RECEIPT.json`. Two release-source scripts remove unused
imports solely to satisfy repository-wide Ruff lint; their portal and release
hashes are recorded in the same receipt. Release-facing metadata and reader
setup files are updated to describe the public v0.2 bundle; the statistical
calculations and result fields are not silently changed.

Before tagging, build the asset, run the full lint/test suite, run a fresh wheel
install on the local platform, and let GitHub Actions complete the Linux,
macOS, and Windows wheel-smoke and Windows full-suite checks. Only a green tag
may be published through the existing trusted-publisher workflow.
