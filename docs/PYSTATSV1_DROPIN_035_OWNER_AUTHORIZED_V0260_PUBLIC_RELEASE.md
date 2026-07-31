# PyStatsV1 Drop-in 035 — Owner-authorized v0.26.0 public release

## Purpose

Drop-in 035 converts the technically proven Psychological Statistics by Design
companion candidate into the exact public PyStatsV1 `0.26.0` distribution. The
unit authorizes only PyPI publication through the repository's existing trusted
publisher, then records and verifies the public wheel and source distribution.

## Approved baseline

- Approved parent main: `400a3d688fb3c341fd393aca715de6d941b7f1e6`
- Release-proof tag: `psych-design-companion-v0-1-release-proof`
- Frozen scientific candidate: `58d92f85b865cb657bf49c731fefc381970c8bda`
- Candidate tag: `psych-design-companion-v0-1-candidate`
- Package release: `pystatsv1==0.26.0`
- Companion release: `v0.1`
- Final annotated tag: `v0.26.0`

The complete Drop-in 034 Ubuntu/WSL proof, all 2,982 governed cross-platform
checks, the deterministic asset identity, and the closed non-PyPI gates remain
unchanged.

## Authorization boundary

The repository owner explicitly authorizes:

1. the exact annotated `v0.26.0` tag;
2. tag CI;
3. manual dispatch of `.github/workflows/pypi-publish.yml`;
4. trusted-publisher upload to PyPI;
5. public wheel and sdist verification; and
6. a post-publication evidence receipt.

The authorization does **not** authorize portal deployment, book binding,
real-data support, scientific changes, package-runtime changes, companion-asset
changes, or edits to the Drop-in 034 proof contract.

## Release gates

Before publication, the source checker requires:

- the complete Drop-in 034 technical-readiness receipt;
- the release-proof tag at the approved parent commit;
- the exact governed companion asset hash;
- the Drop-in 035 owner-authorization receipt;
- an exact allowlisted diff from the approved parent;
- the manual trusted-publisher workflow;
- an annotated tag matching `pyproject.toml`; and
- all portal, book, and real-data gates closed.

The trusted-publisher workflow rebuilds the governed asset, builds the wheel and
sdist with the pinned build backend, verifies both distributions, and publishes
only after all source and authorization checks pass.

## Public verification

After PyPI reports `0.26.0`, the local verifier:

- downloads the wheel and sdist from PyPI;
- verifies their PyPI-reported SHA-256 hashes;
- verifies package name and version metadata;
- verifies the exact embedded companion asset in both artifacts;
- creates a fresh Python 3.10 virtual environment;
- installs `pystatsv1[psych-design]==0.26.0` from the public PyPI index;
- runs `info`, `init`, `verify`, and `doctor`;
- runs the complete SWL-S02 `make first-result` Python/R verification chain;
- verifies the regenerated first-result files; and
- writes `PSYCH_DESIGN_PUBLIC_RELEASE.json` without persisting an absolute
  reader workspace path.

## Final state

A successful unit records:

- public wheel filename, size, and SHA-256;
- public sdist filename, size, and SHA-256;
- exact embedded companion asset identity;
- release commit and annotated tag;
- exact tag-CI and trusted-publisher workflow run IDs;
- successful fresh-public-install command evidence; and
- `pypi_release_authorized: true` with portal, book, and real-data gates false.
