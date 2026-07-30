#!/usr/bin/env python3
"""Deep structural and packaging checks for psych-design companion v0.1 candidate."""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (
    ROOT
    / "psych_design_companion"
    / "psychological_statistics_by_design_companion_v0_1"
)
ASSET = (
    ROOT
    / "src"
    / "pystatsv1"
    / "assets"
    / "psychological_statistics_by_design_companion_v0_1.zip"
)
BUILDER = ROOT / "tools" / "build_psych_design_companion_asset.py"
EXPECTED_STUDIES = [f"SWL-S{number:02d}" for number in range(1, 11)]
FORBIDDEN_PLACEHOLDERS = (
    "to be copied from the governed",
    "target_contract_not_yet_implemented",
    "contract_not_implemented",
    "<actual_release_version>",
    "<actual_companion_directory>",
)
FORBIDDEN_MEMBER_PARTS = {
    "outputs",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".venv",
    "venv",
}
SENSITIVE_NAME_PATTERNS = (
    re.compile(r"(^|/)(\.env|id_rsa|id_ed25519)$", re.IGNORECASE),
    re.compile(r"(^|/)(credentials?|secrets?)(\.|/|$)", re.IGNORECASE),
)


def fail(message: str) -> None:
    raise SystemExit(f"PYSTATSV1_PSYCH_DESIGN_RELEASE_CANDIDATE_ERROR: {message}")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"invalid JSON file {path.relative_to(ROOT)}: {exc}")


def run(command: list[str], *, cwd: Path = ROOT) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    completed = subprocess.run(
        command,
        cwd=cwd,
        env=environment,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        fail(
            "command failed: "
            + " ".join(command)
            + "\n"
            + completed.stdout
            + completed.stderr
        )
    return completed


def validate_registry() -> dict:
    index = load_json(SOURCE / "STUDY_INDEX.json")
    if index.get("schema_version") != "psych-design-study-index-v0.1":
        fail("study-index schema changed")
    if index.get("status") != "release_candidate_implemented_not_public":
        fail("study index incorrectly implies a different lifecycle")
    if index.get("companion_version") != "v0.1":
        fail("companion version changed")
    if index.get("package_release_candidate") != "0.26.0":
        fail("candidate package version changed")
    if index.get("synthetic_only") is not True:
        fail("study index lost the synthetic-only boundary")
    if index.get("real_data_authorized") is not False:
        fail("study index authorizes real data")
    studies = index.get("studies", [])
    if [row.get("study_id") for row in studies] != EXPECTED_STUDIES:
        fail("study index must contain SWL-S01 through SWL-S10 in order")

    path_fields = (
        "dataset_path",
        "design_contract_path",
        "measurement_map_path",
        "python_script",
        "r_launcher",
        "r_script",
        "verification_script",
        "reference_python_result",
    )
    list_path_fields = ("figure_specs", "apa_source_maps", "matched_limitations")
    for row in studies:
        study = row["study_id"]
        for key in path_fields:
            rel = row.get(key)
            if not isinstance(rel, str) or not (SOURCE / rel).is_file():
                fail(f"{study} missing registered path {key}: {rel}")
        for key in list_path_fields:
            values = row.get(key)
            if not isinstance(values, list) or not values:
                fail(f"{study} has no registered {key}")
            for rel in values:
                if not (SOURCE / rel).is_file():
                    fail(f"{study} missing registered {key}: {rel}")
        if row.get("status") != "release_candidate_implemented_not_public":
            fail(f"{study} lifecycle status changed")
        if not row.get("reader_command", "").endswith(study):
            fail(f"{study} reader command is not registry-bound")
        if not row.get("verification_command", "").endswith(study):
            fail(f"{study} verification command is not registry-bound")
        if not row.get("packet_command", "").endswith(study):
            fail(f"{study} packet command is not registry-bound")
        for number_key in (
            "expected_rows",
            "expected_unique_units",
            "expected_unique_keys",
        ):
            if not isinstance(row.get(number_key), int) or row[number_key] <= 0:
                fail(f"{study} has invalid {number_key}")
    return index


def validate_source_tree(index: dict) -> None:
    if not SOURCE.is_dir():
        fail("unified companion source tree is missing")
    text_extensions = {".md", ".json", ".py", ".R", ".txt", ".yaml", ".csv"}
    for path in SOURCE.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(SOURCE).as_posix()
        parts = set(PurePosixPath(rel).parts)
        if parts & FORBIDDEN_MEMBER_PARTS:
            continue
        if any(pattern.search(rel) for pattern in SENSITIVE_NAME_PATTERNS):
            fail(f"sensitive-looking source member is present: {rel}")
        if path.suffix in text_extensions:
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError as exc:
                fail(f"text source is not UTF-8: {rel}: {exc}")
            lowered = text.lower()
            for placeholder in FORBIDDEN_PLACEHOLDERS:
                if placeholder in lowered:
                    fail(f"placeholder text remains in {rel}: {placeholder}")
            if "/home/nicky/" in text or re.search(r"[A-Za-z]:\\Users\\", text):
                fail(f"absolute personal path remains in {rel}")

    lineage = load_json(SOURCE / "SOURCE_LINEAGE.json")
    if lineage.get("source_anchor") != "e88ff0f6f1aa1c4a946c72b97387f47b3c5311ae":
        fail("source-lineage anchor changed")
    if lineage.get("source_batches_preserved_in_place") is not True:
        fail("source lineage no longer records preserved batches")
    if [row.get("study_id") for row in lineage.get("studies", [])] != EXPECTED_STUDIES:
        fail("source lineage does not cover all ten studies")
    for study in lineage["studies"]:
        for origin in study.get("origins", []):
            source_path = ROOT / origin["source_path"]
            companion_path = SOURCE / origin["companion_path"]
            if not source_path.is_file() or not companion_path.is_file():
                fail(f"lineage path missing for {study['study_id']}")
            source_hash = sha256(source_path)
            companion_hash = sha256(companion_path)
            if source_hash != origin["source_sha256"]:
                fail(f"source lineage hash drift for {origin['source_path']}")
            if companion_hash != origin["companion_sha256"]:
                fail(f"companion lineage hash drift for {origin['companion_path']}")
            if origin["transformation"] == "byte-for-byte copy" and (
                source_hash != companion_hash
            ):
                fail(f"byte-for-byte lineage mismatch for {origin['companion_path']}")

    policy = load_json(SOURCE / "VERIFICATION_POLICY.json")
    if policy.get("independent_r_required_for_complete_verification") is not True:
        fail("complete verification no longer requires independent R")
    if [row.get("study_id") for row in policy.get("studies", [])] != EXPECTED_STUDIES:
        fail("verification policy does not cover all ten studies")
    swl8 = next(row for row in policy["studies"] if row["study_id"] == "SWL-S08")
    if swl8.get("verification_category") != "V3_estimand_aligned":
        fail("SWL-S08 V3 estimand-alignment category changed")
    if not swl8.get("v4_documented_not_equal_fields"):
        fail("SWL-S08 has no explicit V4 non-equality documentation")

    provenance = load_json(SOURCE / "COMPANION_PROVENANCE.json")
    if provenance.get("release_status") != "release_candidate_not_public":
        fail("companion provenance implies public release")
    for key in (
        "real_data_authorized",
        "portal_release_authorized",
        "book_binding_authorized",
        "pypi_release_authorized",
    ):
        if provenance.get(key) is not False:
            fail(f"companion provenance opens closed gate: {key}")

    required_templates = {
        "STUDY_MAP.yaml",
        "CLAIM_MAP.yaml",
        "MEASUREMENT_MAP.yaml",
        "DATA_LAYOUT_CONTRACT.yaml",
        "ANALYSIS_PLAN.yaml",
        "VERIFICATION_CONTRACT.yaml",
        "REPORTING_SOURCE_MAP.yaml",
        "MATCHED_LIMITATION.md",
        "ADAPTATION_DELTA_LEDGER.yaml",
    }
    actual_templates = {
        path.name for path in (SOURCE / "templates").iterdir() if path.is_file()
    }
    if actual_templates != required_templates:
        fail(
            "adaptation template set changed "
            f"missing={sorted(required_templates - actual_templates)} "
            f"extra={sorted(actual_templates - required_templates)}"
        )

    expected_entry_scripts = {row["python_script"] for row in index["studies"]}
    if len(expected_entry_scripts) != 10:
        fail("ten distinct visible Python scripts are not registered")


def validate_asset(index: dict) -> None:
    if not ASSET.is_file():
        fail("deterministic packaged asset is missing")
    with zipfile.ZipFile(ASSET) as archive:
        infos = [info for info in archive.infolist() if not info.is_dir()]
        names = [info.filename for info in infos]
        if names != sorted(names[:-1]) + ["COMPANION_MANIFEST.json"]:
            fail("packaged asset member order is not deterministic")
        if len(names) != len(set(names)):
            fail("packaged asset contains duplicate members")
        for info in infos:
            pure = PurePosixPath(info.filename)
            if pure.is_absolute() or ".." in pure.parts or "\\" in info.filename:
                fail(f"unsafe packaged member: {info.filename}")
            if set(pure.parts) & FORBIDDEN_MEMBER_PARTS:
                fail(f"generated or cached packaged member: {info.filename}")
            if any(pattern.search(info.filename) for pattern in SENSITIVE_NAME_PATTERNS):
                fail(f"sensitive-looking packaged member: {info.filename}")
            if info.date_time != (1980, 1, 1, 0, 0, 0):
                fail(f"unstable ZIP timestamp: {info.filename}")
        try:
            manifest = json.loads(archive.read("COMPANION_MANIFEST.json"))
        except (KeyError, json.JSONDecodeError) as exc:
            fail(f"invalid packaged companion manifest: {exc}")
        if manifest.get("schema_version") != (
            "pystatsv1-psych-design-bundle-manifest-v0.1"
        ):
            fail("packaged manifest schema changed")
        if manifest.get("package_version") != "0.26.0":
            fail("packaged manifest package version changed")
        if manifest.get("companion_version") != "v0.1":
            fail("packaged manifest companion version changed")
        if manifest.get("release_status") != "release_candidate_not_public":
            fail("packaged manifest incorrectly implies public release")
        if manifest.get("synthetic_data_only") is not True:
            fail("packaged manifest lost synthetic-only status")
        if manifest.get("real_data_authorized") is not False:
            fail("packaged manifest authorizes real data")
        if manifest.get("study_ids") != EXPECTED_STUDIES:
            fail("packaged manifest study registry changed")
        if manifest.get("first_result_study") != "SWL-S02":
            fail("packaged first-result study changed")
        source_rows = manifest.get("files", [])
        expected_names = {row["path"] for row in source_rows}
        if expected_names | {"COMPANION_MANIFEST.json"} != set(names):
            fail("packaged members differ from manifest")
        for row in source_rows:
            data = archive.read(row["path"])
            if hashlib.sha256(data).hexdigest() != row["sha256"]:
                fail(f"packaged source hash mismatch: {row['path']}")
            expected_mode = "755" if row["path"].startswith(
                ("scripts/python/", "scripts/r/", "scripts/verification/")
            ) else "644"
            if row.get("mode") != expected_mode:
                fail(f"packaged logical mode mismatch: {row['path']}")
        packaged_index = json.loads(archive.read("STUDY_INDEX.json"))
        if packaged_index != index:
            fail("packaged study registry differs from source")

    with tempfile.TemporaryDirectory(prefix="psych-design-determinism-") as temp:
        first = Path(temp) / "first.zip"
        second = Path(temp) / "second.zip"
        run([sys.executable, str(BUILDER), "--dest", str(first)])
        run([sys.executable, str(BUILDER), "--dest", str(second)])
        if sha256(first) != sha256(second) or sha256(first) != sha256(ASSET):
            fail("psych-design companion asset is not exactly reproducible")


def main() -> int:
    index = validate_registry()
    validate_source_tree(index)
    audit = run(
        [
            sys.executable,
            str(SOURCE / "scripts/python/design_audit.py"),
            "--check-only",
        ],
        cwd=SOURCE,
    )
    if "PYSTATSV1_PSYCH_DESIGN_DESIGN_AUDIT_OK studies=10" not in audit.stdout:
        fail("design-audit marker is missing")
    validate_asset(index)
    print(
        "PYSTATSV1_PSYCH_DESIGN_RELEASE_CANDIDATE_VERIFY_OK "
        "studies=10 visible_python=10 r_paths=10 templates=9 package=0.26.0 "
        "companion=v0.1 public=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
