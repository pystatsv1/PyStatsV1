"""PyStatsV1 Book 1 companion launcher and integrity checks.

The launcher provisions a local, inspectable copy of the synthetic-only
*Psych Stats with Python* executable companion. It does not execute analyses,
change source data, or make claims about real-data work.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import stat
import tempfile
import zipfile
from dataclasses import dataclass
from importlib import resources
from pathlib import Path, PurePosixPath
from typing import Final


PKG: Final[str] = "pystatsv1"
ASSET_PACKAGE: Final[str] = f"{PKG}.assets"
ASSET_NAME: Final[str] = "psych_stats_with_python_companion_v0_2.zip"
DEFAULT_DEST_NAME: Final[str] = "psych_stats_with_python_companion_v0_2"
MANIFEST_NAME: Final[str] = "BOOK1_BUNDLE_MANIFEST.json"
MANIFEST_SCHEMA: Final[str] = "pystatsv1-book1-bundle-manifest-v0.1"


@dataclass(frozen=True)
class Book1Verification:
    """Result of checking an extracted Book 1 source snapshot."""

    destination: Path
    companion_version: str
    file_count: int


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _safe_relative(name: str) -> PurePosixPath:
    """Reject archive/member paths that could escape a chosen destination."""
    pure = PurePosixPath(name)
    if not name or pure.is_absolute() or ".." in pure.parts or "." in pure.parts:
        raise ValueError(f"unsafe Book 1 bundle member path: {name!r}")
    if "\\" in name:
        raise ValueError(f"Book 1 bundle member must use POSIX separators: {name!r}")
    return pure


def _asset_path():
    return resources.files(ASSET_PACKAGE) / ASSET_NAME


def _read_manifest_from_zip(zf: zipfile.ZipFile) -> dict:
    try:
        payload = json.loads(zf.read(MANIFEST_NAME).decode("utf-8"))
    except KeyError as exc:
        raise RuntimeError(f"packaged Book 1 asset is missing {MANIFEST_NAME}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"packaged Book 1 asset has invalid {MANIFEST_NAME}") from exc
    if payload.get("schema_version") != MANIFEST_SCHEMA:
        raise RuntimeError("packaged Book 1 asset manifest schema is not supported")
    if payload.get("synthetic_data_only") is not True:
        raise RuntimeError("packaged Book 1 asset does not declare synthetic_data_only=true")
    if not isinstance(payload.get("files"), list) or not payload["files"]:
        raise RuntimeError("packaged Book 1 asset manifest has no source file records")
    return payload


def _validate_zip_members(zf: zipfile.ZipFile, manifest: dict) -> None:
    names: set[str] = set()
    for info in zf.infolist():
        if info.is_dir():
            continue
        _safe_relative(info.filename)
        if stat.S_ISLNK(info.external_attr >> 16):
            raise RuntimeError(f"packaged Book 1 asset contains a symlink: {info.filename}")
        names.add(info.filename)
    expected = {str(row.get("path", "")) for row in manifest["files"]}
    if not expected or any(not name for name in expected):
        raise RuntimeError("packaged Book 1 asset manifest contains an invalid file path")
    if MANIFEST_NAME not in names:
        raise RuntimeError(f"packaged Book 1 asset is missing {MANIFEST_NAME}")
    if expected | {MANIFEST_NAME} != names:
        extra = sorted(names - expected - {MANIFEST_NAME})
        missing = sorted(expected - names)
        pieces = []
        if missing:
            pieces.append("missing: " + ", ".join(missing))
        if extra:
            pieces.append("unexpected: " + ", ".join(extra))
        raise RuntimeError("packaged Book 1 asset members do not match manifest (" + "; ".join(pieces) + ")")
    for row in manifest["files"]:
        name = str(row["path"])
        _safe_relative(name)
        actual = hashlib.sha256(zf.read(name)).hexdigest()
        if actual != row.get("sha256"):
            raise RuntimeError(f"packaged Book 1 asset hash mismatch: {name}")


def packaged_book1_info() -> dict:
    """Read and validate metadata from the installed Book 1 asset."""
    asset = _asset_path()
    with resources.as_file(asset) as asset_path:
        with zipfile.ZipFile(asset_path) as zf:
            manifest = _read_manifest_from_zip(zf)
            _validate_zip_members(zf, manifest)
    return manifest


def initialize_book1(destination: Path) -> Book1Verification:
    """Safely extract the immutable Book 1 asset into a new destination."""
    dest = destination.expanduser().resolve()
    if dest.exists():
        raise RuntimeError(
            f"refusing to overwrite an existing destination: {dest}\n"
            "Choose a new --dest path or inspect the existing folder first."
        )
    dest.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f".{dest.name}.staging-", dir=dest.parent))
    try:
        asset = _asset_path()
        with resources.as_file(asset) as asset_path:
            with zipfile.ZipFile(asset_path) as zf:
                manifest = _read_manifest_from_zip(zf)
                _validate_zip_members(zf, manifest)
                for row in manifest["files"]:
                    name = str(row["path"])
                    rel = _safe_relative(name)
                    output = staging.joinpath(*rel.parts)
                    output.parent.mkdir(parents=True, exist_ok=True)
                    output.write_bytes(zf.read(name))
                    mode = int(str(row.get("mode", "644")), 8)
                    output.chmod(mode)
                (staging / MANIFEST_NAME).write_bytes(zf.read(MANIFEST_NAME))
        verified = verify_book1_directory(staging)
        os.replace(staging, dest)
        return Book1Verification(dest, verified.companion_version, verified.file_count)
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise


def verify_book1_directory(destination: Path) -> Book1Verification:
    """Verify extracted Book 1 source files against their bundled manifest.

    Generated ``outputs/`` files are deliberately outside this immutable-source
    check because students create them while running the companion workflow.
    """
    dest = destination.expanduser().resolve()
    manifest_path = dest / MANIFEST_NAME
    if not manifest_path.is_file():
        raise RuntimeError(f"missing Book 1 bundle manifest: {manifest_path}")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"invalid Book 1 bundle manifest: {manifest_path}") from exc
    if manifest.get("schema_version") != MANIFEST_SCHEMA:
        raise RuntimeError("Book 1 bundle manifest schema is not supported")
    if manifest.get("synthetic_data_only") is not True:
        raise RuntimeError("Book 1 bundle does not declare synthetic_data_only=true")
    companion_version = manifest.get("companion_version")
    if not isinstance(companion_version, str) or not companion_version:
        raise RuntimeError("Book 1 bundle manifest lacks a companion version")
    rows = manifest.get("files")
    if not isinstance(rows, list) or not rows:
        raise RuntimeError("Book 1 bundle manifest has no source file records")
    for row in rows:
        if not isinstance(row, dict):
            raise RuntimeError("Book 1 bundle manifest has an invalid file record")
        rel = _safe_relative(str(row.get("path", "")))
        path = dest.joinpath(*rel.parts)
        if not path.is_file():
            raise RuntimeError(f"Book 1 bundle source file is missing: {rel.as_posix()}")
        expected = row.get("sha256")
        if not isinstance(expected, str) or len(expected) != 64:
            raise RuntimeError(f"Book 1 bundle manifest has invalid hash for: {rel.as_posix()}")
        if _sha256(path) != expected:
            raise RuntimeError(f"Book 1 bundle source file hash mismatch: {rel.as_posix()}")
    return Book1Verification(dest, companion_version, len(rows))
