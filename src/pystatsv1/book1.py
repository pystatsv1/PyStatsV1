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
ASSET_NAME: Final[str] = "psych_stats_with_python_companion_v0_2_1.zip"
DEFAULT_DEST_NAME: Final[str] = "psych_stats_with_python_companion_v0_2_1"
MANIFEST_NAME: Final[str] = "BOOK1_BUNDLE_MANIFEST.json"
MANIFEST_SCHEMA: Final[str] = "pystatsv1-book1-bundle-manifest-v0.1"
CURRENT_COMPANION_VERSION: Final[str] = "v0.2.1"
MAINTENANCE_NAME: Final[str] = "BOOK1_MAINTENANCE_RECEIPT.json"
MAINTENANCE_SCHEMA: Final[str] = "book1-companion-maintenance-receipt-v0.1"
CH08_DATA_PATH: Final[str] = "data/ch08_two_way_anova.csv"


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


def _manifest_hash(manifest: dict, relative: str) -> str:
    for row in manifest["files"]:
        if row.get("path") == relative:
            value = row.get("sha256")
            if isinstance(value, str) and len(value) == 64:
                return value
            break
    raise RuntimeError(f"Book 1 bundle manifest lacks a valid hash for: {relative}")


def _validate_current_maintenance_receipt(data: bytes, manifest: dict) -> None:
    if manifest.get("companion_version") != CURRENT_COMPANION_VERSION:
        return
    try:
        receipt = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError("Book 1 v0.2.1 maintenance receipt is invalid") from exc

    if receipt.get("schema_version") != MAINTENANCE_SCHEMA:
        raise RuntimeError("Book 1 v0.2.1 maintenance receipt schema is not supported")
    if receipt.get("companion_version") != CURRENT_COMPANION_VERSION:
        raise RuntimeError("Book 1 v0.2.1 maintenance receipt version does not match")
    if receipt.get("synthetic_data_only") is not True:
        raise RuntimeError("Book 1 v0.2.1 maintenance receipt must remain synthetic-only")

    release_target = receipt.get("release_target", {})
    expected_target = {
        "package": "pystatsv1",
        "package_version": "0.25.2",
        "companion_version": CURRENT_COMPANION_VERSION,
        "default_destination": DEFAULT_DEST_NAME,
    }
    if release_target != expected_target:
        raise RuntimeError("Book 1 v0.2.1 maintenance release target is invalid")

    correction = receipt.get("correction", {})
    if correction.get("affected_path") != CH08_DATA_PATH:
        raise RuntimeError("Book 1 v0.2.1 maintenance receipt has the wrong affected path")
    if correction.get("new_sha256") != _manifest_hash(manifest, CH08_DATA_PATH):
        raise RuntimeError("Book 1 v0.2.1 corrected CSV hash does not match the bundle manifest")
    if correction.get("old_sha256") == correction.get("new_sha256"):
        raise RuntimeError("Book 1 v0.2.1 maintenance receipt does not record a changed CSV")
    if correction.get("participant_id_sequence") != "ch08_001 through ch08_048":
        raise RuntimeError("Book 1 v0.2.1 participant ID sequence is invalid")

    contract = receipt.get("change_contract", {})
    required_true = {
        "participant_id_changed",
        "strategy_unchanged",
        "feedback_unchanged",
        "test_score_unchanged",
        "row_count_unchanged",
        "row_order_unchanged",
        "cell_membership_unchanged",
        "cell_counts_unchanged",
        "cell_means_unchanged",
        "statistical_analysis_scripts_unchanged",
    }
    if any(contract.get(key) is not True for key in required_true):
        raise RuntimeError("Book 1 v0.2.1 change contract is incomplete")

    data_contract = receipt.get("data_contract_after_correction", {})
    expected_data_contract = {
        "row_count": 48,
        "unique_participant_id_count": 48,
        "duplicate_participant_row_count": 0,
        "cell_count": 4,
        "rows_per_cell": 12,
    }
    if any(data_contract.get(key) != value for key, value in expected_data_contract.items()):
        raise RuntimeError("Book 1 v0.2.1 corrected data contract is invalid")

    statistical = receipt.get("statistical_verification", {})
    required_statistical_true = {
        "python_reported_fields_exactly_unchanged",
        "r_reported_fields_exactly_unchanged",
        "python_r_reported_fields_exactly_equal",
        "chapter12_all_apa_examples_sourced",
        "chapter12_all_parity_receipts_pass",
        "apa_sentence_exactly_unchanged",
    }
    if any(statistical.get(key) is not True for key in required_statistical_true):
        raise RuntimeError("Book 1 v0.2.1 statistical verification is incomplete")
    if statistical.get("chapter8_parity_status") != "PASS":
        raise RuntimeError("Book 1 v0.2.1 Chapter 8 parity is not PASS")

    figure = receipt.get("figure_verification", {})
    if figure.get("byte_identical") is not True or figure.get("figure_count") != 6:
        raise RuntimeError("Book 1 v0.2.1 figure verification is incomplete")

    lineage = receipt.get("lineage", {})
    if lineage.get("historical_portal_handoff_receipt_preserved_unchanged") is not True:
        raise RuntimeError("Book 1 v0.2.1 historical handoff lineage is not preserved")


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
        raise RuntimeError(
            "packaged Book 1 asset members do not match manifest ("
            + "; ".join(pieces)
            + ")"
        )
    for row in manifest["files"]:
        name = str(row["path"])
        _safe_relative(name)
        actual = hashlib.sha256(zf.read(name)).hexdigest()
        if actual != row.get("sha256"):
            raise RuntimeError(f"packaged Book 1 asset hash mismatch: {name}")
    if manifest.get("companion_version") == CURRENT_COMPANION_VERSION:
        if MAINTENANCE_NAME not in names:
            raise RuntimeError(f"packaged Book 1 v0.2.1 asset is missing {MAINTENANCE_NAME}")
        _validate_current_maintenance_receipt(zf.read(MAINTENANCE_NAME), manifest)


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
    if companion_version == CURRENT_COMPANION_VERSION:
        maintenance_path = dest / MAINTENANCE_NAME
        if not maintenance_path.is_file():
            raise RuntimeError(f"Book 1 v0.2.1 bundle is missing {MAINTENANCE_NAME}")
        _validate_current_maintenance_receipt(maintenance_path.read_bytes(), manifest)
    return Book1Verification(dest, companion_version, len(rows))
