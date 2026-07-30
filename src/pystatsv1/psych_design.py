"""Launcher and source verification for the Psychological Statistics by Design companion.

This module provisions and verifies a versioned synthetic-only teaching companion.
It does not choose statistical methods, analyze real data, grant data authorization,
or establish scientific or causal validity.
"""
from __future__ import annotations

import hashlib
import json
import os
import platform
import shutil
import stat
import sys
import tempfile
import zipfile
from dataclasses import dataclass
from importlib import metadata, resources
from pathlib import Path, PurePosixPath
from typing import Final

PKG: Final[str] = "pystatsv1"
ASSET_PACKAGE: Final[str] = f"{PKG}.assets"
ASSET_NAME: Final[str] = "psychological_statistics_by_design_companion_v0_1.zip"
DEFAULT_DEST_NAME: Final[str] = "psychological_statistics_by_design_companion_v0_1"
MANIFEST_NAME: Final[str] = "COMPANION_MANIFEST.json"
MANIFEST_SCHEMA: Final[str] = "pystatsv1-psych-design-bundle-manifest-v0.1"
CURRENT_COMPANION_VERSION: Final[str] = "v0.1"
EXPECTED_PACKAGE_VERSION: Final[str] = "0.26.0"
STUDY_INDEX_NAME: Final[str] = "STUDY_INDEX.json"


@dataclass(frozen=True)
class PsychDesignVerification:
    destination: Path
    companion_version: str
    file_count: int


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _safe_relative(name: str) -> PurePosixPath:
    pure = PurePosixPath(name)
    if not name or pure.is_absolute() or ".." in pure.parts or "." in pure.parts:
        raise ValueError(f"unsafe psych-design bundle member path: {name!r}")
    if "\\" in name:
        raise ValueError(
            f"psych-design bundle member must use POSIX separators: {name!r}"
        )
    return pure


def _asset_path():
    return resources.files(ASSET_PACKAGE) / ASSET_NAME


def _read_manifest_from_zip(zf: zipfile.ZipFile) -> dict:
    try:
        payload = json.loads(zf.read(MANIFEST_NAME).decode("utf-8"))
    except KeyError as exc:
        raise RuntimeError(f"packaged psych-design asset is missing {MANIFEST_NAME}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"packaged psych-design asset has invalid {MANIFEST_NAME}") from exc
    if payload.get("schema_version") != MANIFEST_SCHEMA:
        raise RuntimeError("packaged psych-design manifest schema is not supported")
    if payload.get("companion_version") != CURRENT_COMPANION_VERSION:
        raise RuntimeError("packaged psych-design companion version is not supported")
    if payload.get("package_version") != EXPECTED_PACKAGE_VERSION:
        raise RuntimeError("packaged psych-design package version is not 0.26.0")
    if payload.get("synthetic_data_only") is not True:
        raise RuntimeError("packaged psych-design asset must remain synthetic-only")
    if payload.get("real_data_authorized") is not False:
        raise RuntimeError("packaged psych-design asset may not authorize real data")
    rows = payload.get("files")
    if not isinstance(rows, list) or not rows:
        raise RuntimeError("packaged psych-design manifest has no source file records")
    return payload


def _validate_zip_members(zf: zipfile.ZipFile, manifest: dict) -> None:
    names: set[str] = set()
    for info in zf.infolist():
        if info.is_dir():
            continue
        _safe_relative(info.filename)
        if stat.S_ISLNK(info.external_attr >> 16):
            raise RuntimeError(
                f"packaged psych-design asset contains a symlink: {info.filename}"
            )
        if info.filename in names:
            raise RuntimeError(
                f"packaged psych-design asset contains a duplicate member: {info.filename}"
            )
        names.add(info.filename)
    expected = {str(row.get("path", "")) for row in manifest["files"]}
    if not expected or any(not value for value in expected):
        raise RuntimeError("packaged psych-design manifest contains an invalid path")
    if expected | {MANIFEST_NAME} != names:
        missing = sorted(expected - names)
        extra = sorted(names - expected - {MANIFEST_NAME})
        details = []
        if missing:
            details.append("missing: " + ", ".join(missing))
        if extra:
            details.append("unexpected: " + ", ".join(extra))
        raise RuntimeError(
            "packaged psych-design members do not match manifest ("
            + "; ".join(details)
            + ")"
        )
    for row in manifest["files"]:
        name = str(row["path"])
        _safe_relative(name)
        actual = hashlib.sha256(zf.read(name)).hexdigest()
        if actual != row.get("sha256"):
            raise RuntimeError(f"packaged psych-design asset hash mismatch: {name}")


def packaged_psych_design_info() -> dict:
    asset = _asset_path()
    with resources.as_file(asset) as asset_path:
        with zipfile.ZipFile(asset_path) as zf:
            manifest = _read_manifest_from_zip(zf)
            _validate_zip_members(zf, manifest)
    return manifest


def packaged_study_index() -> dict:
    asset = _asset_path()
    with resources.as_file(asset) as asset_path:
        with zipfile.ZipFile(asset_path) as zf:
            manifest = _read_manifest_from_zip(zf)
            _validate_zip_members(zf, manifest)
            try:
                payload = json.loads(zf.read(STUDY_INDEX_NAME).decode("utf-8"))
            except (KeyError, json.JSONDecodeError) as exc:
                raise RuntimeError("packaged psych-design study index is invalid") from exc
    if payload.get("status") != "release_candidate_implemented_not_public":
        raise RuntimeError("packaged psych-design study index has an invalid lifecycle status")
    studies = payload.get("studies")
    if not isinstance(studies, list) or [row.get("study_id") for row in studies] != [
        f"SWL-S{number:02d}" for number in range(1, 11)
    ]:
        raise RuntimeError("packaged psych-design study index is incomplete")
    return payload


def initialize_psych_design(destination: Path) -> PsychDesignVerification:
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
                    rel = _safe_relative(str(row["path"]))
                    output = staging.joinpath(*rel.parts)
                    output.parent.mkdir(parents=True, exist_ok=True)
                    output.write_bytes(zf.read(rel.as_posix()))
                    output.chmod(int(str(row.get("mode", "644")), 8))
                (staging / MANIFEST_NAME).write_bytes(zf.read(MANIFEST_NAME))
        verified = verify_psych_design_directory(staging)
        os.replace(staging, dest)
        return PsychDesignVerification(
            dest, verified.companion_version, verified.file_count
        )
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise


def verify_psych_design_directory(destination: Path) -> PsychDesignVerification:
    dest = destination.expanduser().resolve()
    manifest_path = dest / MANIFEST_NAME
    if not manifest_path.is_file():
        raise RuntimeError(f"missing psych-design manifest: {manifest_path}")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"invalid psych-design manifest: {manifest_path}") from exc
    if manifest.get("schema_version") != MANIFEST_SCHEMA:
        raise RuntimeError("psych-design manifest schema is not supported")
    if manifest.get("companion_version") != CURRENT_COMPANION_VERSION:
        raise RuntimeError("psych-design companion version is not supported")
    if manifest.get("package_version") != EXPECTED_PACKAGE_VERSION:
        raise RuntimeError("psych-design manifest package version is not 0.26.0")
    if manifest.get("synthetic_data_only") is not True:
        raise RuntimeError("psych-design bundle must remain synthetic-only")
    if manifest.get("real_data_authorized") is not False:
        raise RuntimeError("psych-design bundle may not authorize real data")
    rows = manifest.get("files")
    if not isinstance(rows, list) or not rows:
        raise RuntimeError("psych-design manifest has no source file records")
    for row in rows:
        if not isinstance(row, dict):
            raise RuntimeError("psych-design manifest has an invalid file record")
        rel = _safe_relative(str(row.get("path", "")))
        path = dest.joinpath(*rel.parts)
        if not path.is_file():
            raise RuntimeError(f"psych-design source file is missing: {rel.as_posix()}")
        expected = row.get("sha256")
        if not isinstance(expected, str) or len(expected) != 64:
            raise RuntimeError(
                f"psych-design manifest has invalid hash for: {rel.as_posix()}"
            )
        if _sha256(path) != expected:
            raise RuntimeError(
                f"psych-design source file hash mismatch: {rel.as_posix()}"
            )
    index = json.loads((dest / STUDY_INDEX_NAME).read_text(encoding="utf-8"))
    if len(index.get("studies", [])) != 10:
        raise RuntimeError("psych-design extracted study index is incomplete")
    return PsychDesignVerification(dest, CURRENT_COMPANION_VERSION, len(rows))


def psych_design_doctor(destination: Path) -> dict:
    dest = destination.expanduser().resolve()
    package_version: str
    try:
        package_version = metadata.version(PKG)
    except metadata.PackageNotFoundError:
        package_version = "not installed"
    dependencies = {}
    for module_name, dist_name in (
        ("numpy", "numpy"),
        ("pandas", "pandas"),
        ("scipy", "scipy"),
        ("statsmodels", "statsmodels"),
        ("matplotlib", "matplotlib"),
    ):
        try:
            __import__(module_name)
            dependencies[module_name] = metadata.version(dist_name)
        except Exception:
            dependencies[module_name] = "not installed"
    verification = "not checked"
    source_files = 0
    if dest.is_dir():
        result = verify_psych_design_directory(dest)
        verification = "pass"
        source_files = result.file_count
    return {
        "python_version": platform.python_version(),
        "python_executable": sys.executable,
        "platform": platform.platform(),
        "supported_platform_status": (
            "Ubuntu/WSL proof target; macOS and Windows wheel source checks only"
        ),
        "pystatsv1_version": package_version,
        "companion_version": CURRENT_COMPANION_VERSION,
        "companion_root": str(dest),
        "source_manifest_status": verification,
        "source_file_count": source_files,
        "dependencies": dependencies,
        "rscript_available": shutil.which("Rscript") is not None,
        "rscript_path": shutil.which("Rscript"),
        "synthetic_data_only": True,
        "real_data_authorized": False,
    }
