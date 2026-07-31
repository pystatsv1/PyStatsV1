# PyStatsV1 Drop-in 034 — Clean Ubuntu/WSL Reader Proof and Final Release Freeze

## Boundary

This PyStatsV1-only unit starts from `58d92f85b865cb657bf49c731fefc381970c8bda` and the candidate tag
`psych-design-companion-v0-1-candidate`. It adds proof contracts, portable clean-reader runners,
machine-readable receipts, cross-platform comparison, and publication-gate
tests. It does not change the governed companion source or asset, create
`v0.26.0`, publish to PyPI, edit the portal or book, or authorize real data.

## Two-stage closure

Stage 1 runs a fresh native-Ubuntu proof from the canonical wheel, confirms the
candidate source remains byte-frozen, builds the same source wheel twice as a
clean regeneration check, commits the Ubuntu evidence, and exports a WSL kit.
It deliberately stops before opening a pull request.

The WSL kit must be unpacked inside the WSL Linux home rather than `/mnt/c`.
It requires Windows 11 WSL2 rather than WSL1, records Windows, WSL, Ubuntu,
kernel, Python, pip, R, Rscript, R session, `nlme`, package, companion,
manifest, study and output facts, and stores only Linux-home-relative workspace
information in committed receipts. It runs SWL-S01
through SWL-S10 in Python and independent R paths.

Stage 2 validates the WSL result, compares exact scientific evidence with the
Ubuntu receipt, allows only explicitly recorded PNG renderer differences, and
sets `technical_release_ready` only when every required comparison passes. The
publication, portal, book-binding and real-data authorization fields remain
false.

## Frozen artifact identities

- canonical wheel: `pystatsv1-0.26.0-py3-none-any.whl`
- canonical wheel SHA-256: `62a5c26577867f22c7bbf15dcf4253da749fe703fcec42ffc19b72454af8fa05`
- packaged companion asset SHA-256: `bd0932c1d126758f37fab180173d6b95b5e4c31bc654724251aa6eb6296243c1`
- immutable source files: 151
- companion version: `v0.1`
- package version: `0.26.0`

## Final proof tag

A successful Drop-in 034 may create `psych-design-companion-v0-1-release-proof`. The public release tag
`v0.26.0` remains reserved for a later explicitly authorized PyPI release.
