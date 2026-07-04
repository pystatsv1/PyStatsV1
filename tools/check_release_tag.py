#!/usr/bin/env python3
"""Verify that an annotated release tag exactly matches pyproject metadata."""

from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path


class ReleaseCheckError(RuntimeError):
    """Raised when the checked-out source is not a publishable release tag."""


def _git(repo: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=False,
        text=True,
        capture_output=True,
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip() or "unknown git error"
        raise ReleaseCheckError(detail)
    return completed.stdout.strip()


def project_version(repo: Path) -> str:
    """Read the simple PEP 621 project version without requiring a TOML dependency."""
    text = (repo / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r'^version\s*=\s*"([^"]+)"\s*$', text, flags=re.MULTILINE)
    if not match:
        raise ReleaseCheckError("could not read [project] version from pyproject.toml")
    return match.group(1)


def verify_release_tag(repo: Path) -> tuple[str, str]:
    """Return the exact annotated tag and version when they are a safe match."""
    repo = repo.resolve()
    version = project_version(repo)
    expected_tag = f"v{version}"
    head = _git(repo, "rev-parse", "HEAD")
    tag = _git(repo, "describe", "--tags", "--exact-match", "HEAD")

    if tag != expected_tag:
        raise ReleaseCheckError(
            f"checked-out tag {tag!r} does not match pyproject version {version!r}; "
            f"expected {expected_tag!r}"
        )

    object_type = _git(repo, "cat-file", "-t", f"refs/tags/{tag}")
    if object_type != "tag":
        raise ReleaseCheckError(f"{tag} must be an annotated tag, found {object_type!r}")

    tagged_commit = _git(repo, "rev-parse", f"{tag}^{{commit}}")
    if tagged_commit != head:
        raise ReleaseCheckError(f"{tag} does not resolve to checked-out HEAD")

    return tag, version


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd(), help="repository root (default: current directory)")
    args = parser.parse_args()
    try:
        tag, version = verify_release_tag(args.repo)
    except (OSError, ReleaseCheckError) as exc:
        print(f"PYSTATSV1_RELEASE_TAG_VERSION_CHECK_FAILED: {exc}")
        return 1
    print(f"PYSTATSV1_RELEASE_TAG_VERSION_OK tag={tag} version={version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
