#!/usr/bin/env python3
"""Build the deterministic Psychological Statistics by Design companion asset."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import subprocess
import sys
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "psych_design_companion" / "psychological_statistics_by_design_companion_v0_1"
DEFAULT_DEST = ROOT / "src" / "pystatsv1" / "assets" / "psychological_statistics_by_design_companion_v0_1.zip"
MANIFEST_NAME = "COMPANION_MANIFEST.json"
SCHEMA_VERSION = "pystatsv1-psych-design-bundle-manifest-v0.1"
COMPANION_VERSION = "v0.1"
PACKAGE_VERSION = "0.26.0"
EXCLUDED_DIRS = {"outputs", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".venv", "venv"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo", ".swp", "~"}
REQUIRED_FILES = {
    "README.md",
    "LICENSE_NOTES.md",
    "Makefile",
    "COMPANION_PROVENANCE.json",
    "SOURCE_LINEAGE.json",
    "STUDY_INDEX.json",
    "VERIFICATION_POLICY.json",
    "requirements-psych-design-companion.txt",
    "scripts/python/companion_runtime.py",
    "scripts/python/run_study.py",
    "scripts/python/run_all.py",
    "scripts/python/design_audit.py",
    "scripts/python/generate_figures.py",
    "scripts/python/build_reviewer_packet.py",
    "scripts/r/run_study.R",
    "scripts/r/run_all.R",
    "scripts/verification/verify_study.py",
    "scripts/verification/verify_all.py",
    "templates/ADAPTATION_DELTA_LEDGER.yaml",
}
FORBIDDEN_TEXT = (
    "to be copied from the governed",
    "target_contract_not_yet_implemented",
    "contract_not_implemented",
)


def _safe_relative(path: Path, source: Path) -> str:
    relative = path.relative_to(source).as_posix()
    pure = PurePosixPath(relative)
    if not relative or pure.is_absolute() or ".." in pure.parts:
        raise ValueError(f"unsafe source path: {relative!r}")
    return relative


def _include(path: Path, source: Path) -> bool:
    relative = Path(_safe_relative(path, source))
    if any(part in EXCLUDED_DIRS for part in relative.parts):
        return False
    if path.suffix in EXCLUDED_SUFFIXES:
        return False
    if relative.as_posix() == MANIFEST_NAME:
        return False
    return True


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"invalid JSON source file: {path}") from exc


def _logical_mode(relative: str) -> int:
    if relative.startswith(("scripts/python/", "scripts/r/", "scripts/verification/")):
        return 0o755
    return 0o644


def _source_entries(source: Path) -> list[tuple[str, bytes, int]]:
    entries = []
    paths = [path for path in source.rglob("*") if path.is_file()]
    for path in sorted(paths, key=lambda item: _safe_relative(item, source)):
        if not _include(path, source):
            continue
        relative = _safe_relative(path, source)
        entries.append((relative, path.read_bytes(), _logical_mode(relative)))
    return entries


def _validate_source(source: Path) -> dict:
    if not source.is_dir():
        raise SystemExit(f"missing psych-design companion source: {source}")
    names = {
        _safe_relative(path, source)
        for path in source.rglob("*")
        if path.is_file() and _include(path, source)
    }
    missing = sorted(REQUIRED_FILES - names)
    if missing:
        raise SystemExit("psych-design companion source is incomplete:\n" + "\n".join(missing))
    index = _load_json(source / "STUDY_INDEX.json")
    if index.get("companion_version") != COMPANION_VERSION:
        raise SystemExit("psych-design study index companion version is invalid")
    if index.get("package_release_candidate") != PACKAGE_VERSION:
        raise SystemExit("psych-design study index package version is invalid")
    if index.get("status") != "release_candidate_implemented_not_public":
        raise SystemExit("psych-design study index lifecycle status is invalid")
    if index.get("synthetic_only") is not True or index.get("real_data_authorized") is not False:
        raise SystemExit("psych-design study index data boundary is invalid")
    studies = index.get("studies", [])
    expected_ids = [f"SWL-S{number:02d}" for number in range(1, 11)]
    if [row.get("study_id") for row in studies] != expected_ids:
        raise SystemExit("psych-design study index must contain SWL-S01 through SWL-S10")
    text = (source / "STUDY_INDEX.json").read_text(encoding="utf-8").lower()
    for forbidden in FORBIDDEN_TEXT:
        if forbidden in text:
            raise SystemExit(f"psych-design study index retains placeholder text: {forbidden}")
    for row in studies:
        required = {
            row["dataset_path"], row["design_contract_path"], row["measurement_map_path"],
            row["python_script"], row["r_script"], row["verification_script"],
            row["reference_python_result"], *row["figure_specs"], *row["apa_source_maps"], *row["matched_limitations"],
        }
        absent = sorted(path for path in required if path not in names)
        if absent:
            raise SystemExit(f"{row['study_id']} registry paths are missing:\n" + "\n".join(absent))
    provenance = _load_json(source / "COMPANION_PROVENANCE.json")
    expected_false = (
        "real_data_authorized", "portal_release_authorized", "book_binding_authorized", "pypi_release_authorized"
    )
    if any(provenance.get(key) is not False for key in expected_false):
        raise SystemExit("psych-design source opens a closed lifecycle gate")
    if provenance.get("release_status") != "release_candidate_not_public":
        raise SystemExit("psych-design source incorrectly implies public release")
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    completed = subprocess.run(
        [sys.executable, str(source / "scripts/python/design_audit.py"), "--check-only"],
        cwd=source,
        env=environment,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0 or "PYSTATSV1_PSYCH_DESIGN_DESIGN_AUDIT_OK" not in completed.stdout:
        raise SystemExit("psych-design source design audit failed:\n" + completed.stdout + completed.stderr)
    return index


def _manifest(entries: list[tuple[str, bytes, int]], index: dict) -> bytes:
    payload = {
        "schema_version": SCHEMA_VERSION,
        "companion_version": COMPANION_VERSION,
        "package_version": PACKAGE_VERSION,
        "release_status": "release_candidate_not_public",
        "synthetic_data_only": True,
        "real_data_authorized": False,
        "study_ids": [row["study_id"] for row in index["studies"]],
        "first_result_study": "SWL-S02",
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
    index = _validate_source(source)
    entries = _source_entries(source)
    manifest = _manifest(entries, index)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(dest, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for name, data, mode in entries:
            zf.writestr(_zip_info(name, mode), data)
        zf.writestr(_zip_info(MANIFEST_NAME, 0o644), manifest)
    print(
        f"PYSTATSV1_PSYCH_DESIGN_ASSET_BUILT companion={COMPANION_VERSION} "
        f"source_files={len(entries)} dest={dest}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--dest", type=Path, default=DEFAULT_DEST)
    args = parser.parse_args()
    build(args.source, args.dest)


if __name__ == "__main__":
    main()
