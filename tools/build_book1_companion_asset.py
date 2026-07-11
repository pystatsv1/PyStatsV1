#!/usr/bin/env python3
"""Build the deterministic PyStatsV1 Book 1 companion asset.

The v0.2.1 source snapshot under ``book1_companion/`` is the current
PyStatsV1-side source of truth. Historical snapshots remain rebuildable by
passing explicit ``--source`` and ``--dest`` paths.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import stat
import subprocess
import sys
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "book1_companion" / "psych_stats_with_python_companion_v0_2_1"
DEFAULT_DEST = ROOT / "src" / "pystatsv1" / "assets" / "psych_stats_with_python_companion_v0_2_1.zip"
MANIFEST_NAME = "BOOK1_BUNDLE_MANIFEST.json"
SCHEMA_VERSION = "pystatsv1-book1-bundle-manifest-v0.1"
CURRENT_COMPANION_VERSION = "v0.2.1"
MAINTENANCE_NAME = "BOOK1_MAINTENANCE_RECEIPT.json"
MAINTENANCE_SCHEMA = "book1-companion-maintenance-receipt-v0.1"
CH08_DATA_PATH = "data/ch08_two_way_anova.csv"
DESIGN_CONTRACT_NAME = "BOOK1_DESIGN_CONTRACT.json"
DESIGN_AUDIT_LIBRARY = "scripts/python/book1_design_contract.py"
DESIGN_AUDIT_COMMAND = "scripts/python/audit_design_contract.py"
DESIGN_AUDIT_TESTS = "tests/test_book1_design_contract.py"
DESIGN_AUDIT_SUCCESS_MARKER = "BOOK1_COMPANION_DESIGN_AUDIT_OK"
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
VERSION_REQUIRED_FILES = {
    CURRENT_COMPANION_VERSION: {
        MAINTENANCE_NAME,
        DESIGN_CONTRACT_NAME,
        DESIGN_AUDIT_LIBRARY,
        DESIGN_AUDIT_COMMAND,
        DESIGN_AUDIT_TESTS,
    },
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


def _load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"invalid JSON source file: {path}") from exc


def _validate_current_maintenance(source: Path, provenance: dict) -> None:
    if provenance.get("companion_version") != CURRENT_COMPANION_VERSION:
        return

    receipt_path = source / MAINTENANCE_NAME
    receipt = _load_json(receipt_path)

    if receipt.get("schema_version") != MAINTENANCE_SCHEMA:
        raise SystemExit("Book 1 v0.2.1 maintenance receipt schema is invalid")
    if receipt.get("companion_version") != CURRENT_COMPANION_VERSION:
        raise SystemExit("Book 1 v0.2.1 maintenance receipt version is invalid")
    if receipt.get("synthetic_data_only") is not True:
        raise SystemExit("Book 1 v0.2.1 maintenance receipt must remain synthetic-only")

    target = receipt.get("release_target", {})
    expected_target = {
        "package": "pystatsv1",
        "package_version": "0.25.2",
        "companion_version": CURRENT_COMPANION_VERSION,
        "default_destination": "psych_stats_with_python_companion_v0_2_1",
    }
    if target != expected_target:
        raise SystemExit("Book 1 v0.2.1 maintenance release target is invalid")

    correction = receipt.get("correction", {})
    if correction.get("affected_path") != CH08_DATA_PATH:
        raise SystemExit("Book 1 v0.2.1 maintenance affected path is invalid")

    actual_csv_hash = _sha256_bytes((source / CH08_DATA_PATH).read_bytes())
    if correction.get("new_sha256") != actual_csv_hash:
        raise SystemExit("Book 1 v0.2.1 maintenance CSV hash does not match source")
    if correction.get("old_sha256") == correction.get("new_sha256"):
        raise SystemExit("Book 1 v0.2.1 maintenance receipt does not record a changed CSV")

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
        raise SystemExit("Book 1 v0.2.1 change contract is incomplete")

    data_contract = receipt.get("data_contract_after_correction", {})
    expected_data = {
        "row_count": 48,
        "unique_participant_id_count": 48,
        "duplicate_participant_row_count": 0,
        "cell_count": 4,
        "rows_per_cell": 12,
    }
    if any(data_contract.get(key) != value for key, value in expected_data.items()):
        raise SystemExit("Book 1 v0.2.1 corrected data contract is invalid")

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
        raise SystemExit("Book 1 v0.2.1 statistical verification is incomplete")
    if statistical.get("chapter8_parity_status") != "PASS":
        raise SystemExit("Book 1 v0.2.1 Chapter 8 parity is not PASS")

    figure = receipt.get("figure_verification", {})
    if figure.get("byte_identical") is not True or figure.get("figure_count") != 6:
        raise SystemExit("Book 1 v0.2.1 figure verification is incomplete")

    lineage = receipt.get("lineage", {})
    if lineage.get("historical_portal_handoff_receipt_preserved_unchanged") is not True:
        raise SystemExit("Book 1 v0.2.1 historical handoff lineage is not preserved")


def _validate_current_design_audit(source: Path, provenance: dict) -> None:
    if provenance.get("companion_version") != CURRENT_COMPANION_VERSION:
        return

    command_path = source / DESIGN_AUDIT_COMMAND
    completed = subprocess.run(
        [
            sys.executable,
            str(command_path),
            "--root",
            str(source),
            "--check-only",
        ],
        cwd=source,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    output = completed.stdout + completed.stderr
    if completed.returncode != 0:
        raise SystemExit(
            "Book 1 v0.2.1 design audit failed before asset build:\n" + output
        )
    if DESIGN_AUDIT_SUCCESS_MARKER not in completed.stdout:
        raise SystemExit(
            "Book 1 v0.2.1 design audit did not emit its success marker:\n"
            + output
        )


def _source_entries(source: Path) -> list[tuple[str, bytes, int]]:
    entries: list[tuple[str, bytes, int]] = []
    paths = [path for path in source.rglob("*") if path.is_file()]
    for path in sorted(paths, key=lambda candidate: _safe_relative(candidate, source)):
        if not _include(path, source):
            continue
        relative = _safe_relative(path, source)
        data = path.read_bytes()
        mode = 0o755 if relative.startswith(("scripts/python/", "scripts/r/")) else 0o644
        entries.append((relative, data, mode))
    return entries


def _manifest(entries: list[tuple[str, bytes, int]], source: Path) -> bytes:
    provenance = _load_json(source / "BOOK1_SOURCE_PROVENANCE.json")
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

    provenance = _load_json(source / "BOOK1_SOURCE_PROVENANCE.json")
    companion_version = provenance.get("companion_version")
    if not isinstance(companion_version, str) or not companion_version:
        raise SystemExit("Book 1 source provenance lacks a companion version")
    if provenance.get("synthetic_data_only") is not True:
        raise SystemExit("Book 1 source provenance must declare synthetic_data_only=true")

    entries = _source_entries(source)
    names = {name for name, _, _ in entries}
    required = set(REQUIRED_FILES)
    required.update(VERSION_REQUIRED_FILES.get(companion_version, set()))
    missing = sorted(required - names)
    if missing:
        raise SystemExit(
            "Book 1 companion source is incomplete:\n"
            + "\n".join(f"- {name}" for name in missing)
        )
    if MANIFEST_NAME in names:
        raise SystemExit(
            f"{MANIFEST_NAME} is generated and must not be tracked in source snapshot"
        )

    _validate_current_maintenance(source, provenance)
    _validate_current_design_audit(source, provenance)

    manifest = _manifest(entries, source)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(
        dest,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as zf:
        for name, data, mode in entries:
            zf.writestr(_zip_info(name, mode), data)
        zf.writestr(_zip_info(MANIFEST_NAME, 0o644), manifest)
    print(
        f"PYSTATSV1_BOOK1_ASSET_BUILT companion_version={companion_version} "
        f"files={len(entries)} dest={dest}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--dest", type=Path, default=DEFAULT_DEST)
    args = parser.parse_args()
    build(args.source, args.dest)


if __name__ == "__main__":
    main()
