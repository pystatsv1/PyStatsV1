#!/usr/bin/env python3
"""Build the deterministic PyStatsV1 Book 1 companion asset.

The v0.2 source snapshot under book1_companion/ is the PyStatsV1-side source
of truth for the package asset. The archive contains only synthetic teaching
materials and a manifest of the source files it provisions.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import stat
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "book1_companion" / "psych_stats_with_python_companion_v0_2"
DEFAULT_DEST = ROOT / "src" / "pystatsv1" / "assets" / "psych_stats_with_python_companion_v0_2.zip"
MANIFEST_NAME = "BOOK1_BUNDLE_MANIFEST.json"
SCHEMA_VERSION = "pystatsv1-book1-bundle-manifest-v0.1"
EXCLUDED_DIRS = {"__pycache__", ".pytest_cache", ".git"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo"}
REQUIRED_FILES = {
    "README.md",
    "LICENSE_NOTES.md",
    "Makefile",
    "requirements-book1-companion.txt",
    "figures_specs.json",
    "BOOK1_SOURCE_PROVENANCE.json",
    "BOOK1_PORTAL_HANDOFF_RECEIPT.json",
    "data/ch05_independent.csv",
    "data/ch06_paired.csv",
    "data/ch07_one_way_anova.csv",
    "data/ch08_two_way_anova.csv",
    "data/ch09_repeated_measures.csv",
    "data/ch10_correlation.csv",
    "data/ch11_regression.csv",
    "scripts/python/generate_figures.py",
    "scripts/python/run_all.py",
    "scripts/python/compare_results.py",
    "scripts/r/run_all.R",
}


def _safe_relative(path: Path, source: Path) -> str:
    relative = path.relative_to(source).as_posix()
    pure = PurePosixPath(relative)
    if pure.is_absolute() or ".." in pure.parts or not relative:
        raise ValueError(f"unsafe source path: {relative!r}")
    return relative


def _include(path: Path, source: Path) -> bool:
    relative = Path(_safe_relative(path, source))
    if any(part in EXCLUDED_DIRS for part in relative.parts):
        return False
    if path.suffix in EXCLUDED_SUFFIXES:
        return False
    if relative.parts and relative.parts[0] == "outputs":
        return False
    return True


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _source_entries(source: Path) -> list[tuple[str, bytes, int]]:
    entries: list[tuple[str, bytes, int]] = []
    # Sort by the POSIX archive member name, not by Path objects. Path ordering
    # is platform-dependent (notably case-insensitive on Windows), while the
    # bundle manifest and archive must be byte-stable on every supported host.
    paths = [path for path in source.rglob("*") if path.is_file()]
    for path in sorted(paths, key=lambda candidate: _safe_relative(candidate, source)):
        if not _include(path, source):
            continue
        relative = _safe_relative(path, source)
        data = path.read_bytes()
        # Git for Windows does not preserve POSIX executable bits. Archive modes
        # are therefore a versioned bundle contract, not a host-filesystem fact.
        mode = 0o755 if relative.startswith(("scripts/python/", "scripts/r/")) else 0o644
        entries.append((relative, data, mode))
    return entries


def _manifest(entries: list[tuple[str, bytes, int]], source: Path) -> bytes:
    provenance = json.loads((source / "BOOK1_SOURCE_PROVENANCE.json").read_text(encoding="utf-8"))
    payload = {
        "schema_version": SCHEMA_VERSION,
        "companion_version": provenance["companion_version"],
        "synthetic_data_only": True,
        "source_provenance": provenance,
        "files": [
            {"path": name, "sha256": _sha256_bytes(data), "mode": f"{mode:o}"}
            for name, data, mode in entries
        ],
    }
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _zip_info(name: str, mode: int) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
    info.create_system = 3
    info.external_attr = ((stat.S_IFREG | mode) & 0xFFFF) << 16
    info.compress_type = zipfile.ZIP_DEFLATED
    return info


def build(source: Path, dest: Path) -> None:
    source = source.resolve()
    if not source.is_dir():
        raise SystemExit(f"missing Book 1 companion source: {source}")
    entries = _source_entries(source)
    names = {name for name, _, _ in entries}
    missing = sorted(REQUIRED_FILES - names)
    if missing:
        raise SystemExit("Book 1 companion source is incomplete:\n" + "\n".join(f"- {name}" for name in missing))
    if MANIFEST_NAME in names:
        raise SystemExit(f"{MANIFEST_NAME} is generated and must not be tracked in source snapshot")
    manifest = _manifest(entries, source)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(dest, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for name, data, mode in entries:
            zf.writestr(_zip_info(name, mode), data)
        zf.writestr(_zip_info(MANIFEST_NAME, 0o644), manifest)
    print(f"PYSTATSV1_BOOK1_ASSET_BUILT {dest}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--dest", type=Path, default=DEFAULT_DEST)
    args = parser.parse_args()
    build(args.source, args.dest)


if __name__ == "__main__":
    main()
