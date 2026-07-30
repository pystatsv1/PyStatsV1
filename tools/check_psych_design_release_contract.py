#!/usr/bin/env python3
"""Verify the frozen psych-design contract and its implemented release candidate."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10
    import tomli as tomllib

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_ROOT = ROOT / "psych_design_companion/psych_design_release_contract_v0_1"
SOURCE_ROOT = (
    ROOT
    / "psych_design_companion"
    / "psychological_statistics_by_design_companion_v0_1"
)
EXPECTED = {
    "COMPANION_RELEASE_CONTRACT.json",
    "COMMAND_INTERFACE_CONTRACT.json",
    "CURRENT_STUDY_ASSET_INVENTORY.json",
    "TARGET_STUDY_INDEX.json",
    "CROSS_REPOSITORY_GAP_MATRIX.json",
    "CROSS_REPOSITORY_AUDIT_ANCHORS.json",
    "SOURCE_BATCH_PRESERVATION_MANIFEST.json",
    "PUBLIC_ASSET_LICENSE_CONTRACT.json",
    "README.md",
}
EXPECTED_STUDIES = [f"SWL-S{number:02d}" for number in range(1, 11)]
CLOSED_GATES = (
    "public_companion_released",
    "pypi_release_authorized",
    "portal_release_authorized",
    "real_data_authorized",
    "book_binding_authorized",
)


def fail(message: str) -> None:
    raise SystemExit(f"PYSTATSV1_PSYCH_DESIGN_RELEASE_CONTRACT_ERROR: {message}")


def read(name: str) -> dict:
    path = CONTRACT_ROOT / name
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot read {path.relative_to(ROOT)}: {exc}")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_preservation() -> None:
    preservation = read("SOURCE_BATCH_PRESERVATION_MANIFEST.json")
    total = 0
    for batch in preservation["batches"]:
        actual_rows = []
        for row in batch["files"]:
            path = ROOT / row["path"]
            if not path.is_file():
                fail(f"preserved source file missing: {row['path']}")
            if path.stat().st_size != row["bytes"] or digest(path) != row["sha256"]:
                fail(f"preserved source file drift: {row['path']}")
            actual_rows.append(f"{row['sha256']}  {row['path']}\n")
        tree = hashlib.sha256("".join(actual_rows).encode()).hexdigest()
        if tree != batch["tree_sha256"] or len(actual_rows) != batch["file_count"]:
            fail(f"preserved source tree drift: {batch['batch_root']}")
        total += len(actual_rows)
    if total != 136:
        fail(f"preserved source file total changed: {total}")


def main() -> int:
    if not CONTRACT_ROOT.is_dir():
        fail("contract root is missing")
    names = {path.name for path in CONTRACT_ROOT.iterdir() if path.is_file()}
    if names != EXPECTED:
        fail(
            "contract member set changed "
            f"missing={sorted(EXPECTED - names)} extra={sorted(names - EXPECTED)}"
        )

    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))[
        "project"
    ]
    if project.get("version") != "0.26.0":
        fail("release-candidate package version is not 0.26.0")
    extra = project.get("optional-dependencies", {}).get("psych-design")
    expected_extra = {
        "numpy==2.2.6",
        "pandas==2.2.3",
        "scipy==1.15.3",
        "statsmodels==0.14.6",
        "matplotlib==3.10.8",
    }
    if set(extra or []) != expected_extra:
        fail("psych-design optional dependency set changed")

    release = read("COMPANION_RELEASE_CONTRACT.json")
    expected_baseline = {
        "main_commit": "6cd680812c7a149d4909eff4ddaf6e1679f6aba1",
        "package_version": "0.25.2",
        "repository": "PyStatsV1",
    }
    if release.get("baseline") != expected_baseline:
        fail("Drop-in 032 baseline identity changed")
    if release.get("release_candidate_baseline_main") != (
        "e88ff0f6f1aa1c4a946c72b97387f47b3c5311ae"
    ):
        fail("Drop-in 033 baseline identity is missing or changed")
    planned = release["planned_release"]
    required = {
        "package_version": "0.26.0",
        "release_tag": "v0.26.0",
        "optional_extra": "psych-design",
        "cli_namespace": "psych-design",
        "companion_version": "v0.1",
        "default_destination": "psychological_statistics_by_design_companion_v0_1",
        "asset_name": "psychological_statistics_by_design_companion_v0_1.zip",
    }
    for key, value in required.items():
        if planned.get(key) != value:
            fail(f"planned release field changed: {key}")
    life = release["lifecycle"]
    if life.get("contract_frozen") is not True:
        fail("contract is not frozen")
    if life.get("release_candidate_implemented") is not True:
        fail("release candidate is not recorded as implemented")
    for key in CLOSED_GATES:
        if life.get(key) is not False:
            fail(f"closed lifecycle gate changed: {key}")
    if release.get("study_ids") != EXPECTED_STUDIES:
        fail("study ID registry is incomplete or out of order")
    if release.get("first_result_study") != "SWL-S02":
        fail("first-result study changed")
    for rel in (release["release_candidate_source"], release["release_candidate_asset"]):
        if not (ROOT / rel).exists():
            fail(f"release-candidate path is missing: {rel}")

    commands = read("COMMAND_INTERFACE_CONTRACT.json")
    if commands.get("status") != "release_candidate_implemented_not_public":
        fail("command status does not identify the non-public release candidate")
    if commands.get("package_install") != (
        'python -m pip install "pystatsv1[psych-design]==0.26.0"'
    ):
        fail("planned install command changed")
    if any(row.get("implemented") is not True for row in commands.get("commands", [])):
        fail("an implemented candidate command is marked unavailable")
    expected_commands = {
        "pystatsv1 psych-design info",
        "pystatsv1 psych-design init",
        "pystatsv1 psych-design verify --dest .",
        "pystatsv1 psych-design list-studies",
        "pystatsv1 psych-design doctor --dest .",
    }
    if {row["command"] for row in commands["commands"]} != expected_commands:
        fail("command family changed")
    cli = (ROOT / "src/pystatsv1/cli.py").read_text(encoding="utf-8")
    if '"psych-design"' not in cli or "cmd_psych_design_doctor" not in cli:
        fail("psych-design CLI implementation is missing")

    inventory = read("CURRENT_STUDY_ASSET_INVENTORY.json")["studies"]
    if {row["study_id"] for row in inventory} != set(EXPECTED_STUDIES):
        fail("current study inventory is incomplete")
    for row in inventory:
        for key in (
            "dataset_path",
            "design_contract_path",
            "current_python_implementation",
            "current_r_script",
            "current_verification_script",
            "python_result_receipt",
        ):
            if not (ROOT / row[key]).is_file():
                fail(f"{row['study_id']} missing {key}: {row[key]}")
        for key in ("figure_sources", "apa_source_maps", "matched_limitations"):
            for rel in row[key]:
                if not (ROOT / rel).is_file():
                    fail(f"{row['study_id']} missing {key}: {rel}")
        if row.get("current_public_release") is not False:
            fail(f"{row['study_id']} source batch incorrectly implies public release")

    target = read("TARGET_STUDY_INDEX.json")
    actual_path = ROOT / target.get("actual_registry", "")
    if target.get("status") != "release_candidate_implemented_not_public":
        fail("target study index lifecycle status changed")
    if not actual_path.is_file() or digest(actual_path) != target.get(
        "actual_registry_sha256"
    ):
        fail("target study index is not bound to the actual registry")
    actual = json.loads(actual_path.read_text(encoding="utf-8"))
    if target.get("studies") != actual.get("studies"):
        fail("contract registry mirror differs from the companion registry")
    if [row.get("study_id") for row in actual["studies"]] != EXPECTED_STUDIES:
        fail("actual study registry is incomplete or out of order")
    if any(row.get("status") != "release_candidate_implemented_not_public" for row in actual["studies"]):
        fail("actual study registry opens an invalid lifecycle status")

    verify_preservation()

    gaps = read("CROSS_REPOSITORY_GAP_MATRIX.json")["rows"]
    required_areas = {
        "Source studies",
        "CLI and PyPI extra",
        "Visible per-study Python scripts",
        "R verification",
        "Study registry",
        "Measurement maps",
        "Reviewer packets",
        "Licensing",
        "Portal",
        "Book interior",
        "Clean reader proofs",
    }
    if {row["area"] for row in gaps} != required_areas:
        fail("cross-repository gap matrix is incomplete")
    deferred = {row["area"]: row for row in gaps}
    if "deferred" not in deferred["Book interior"]["gap"].lower():
        fail("book edits are not clearly deferred")
    if "no route" not in deferred["Portal"]["gap"].lower():
        fail("portal release is not clearly deferred")

    license_contract = read("PUBLIC_ASSET_LICENSE_CONTRACT.json")
    if license_contract.get("current_repository_license") != "MIT" or not (
        ROOT / "LICENSE"
    ).is_file():
        fail("repository license boundary changed")
    if license_contract.get("real_data_included") is not False:
        fail("public asset real-data exclusion changed")
    if license_contract.get("book_prose_included") is not False:
        fail("public asset book-prose exclusion changed")

    anchors = read("CROSS_REPOSITORY_AUDIT_ANCHORS.json")["attachments"]
    if anchors["book"]["archive_commit"] != (
        "ec14f859f4ce686ec0091f879382b5ac5bfaf5b3"
    ):
        fail("book audit anchor changed")
    if anchors["book"]["tests_passed"] != 676 or anchors["book"]["paperback_pages"] != 131:
        fail("book proof anchor changed")
    if anchors["portal"]["archive_commit"] != (
        "b9c0f3a1a6dd4392e6e877d75b3c7d73aa249811"
    ):
        fail("portal audit anchor changed")

    print(
        "PYSTATSV1_PSYCH_DESIGN_RELEASE_CONTRACT_VERIFY_OK "
        "studies=10 source_batches=3 package=0.26.0 companion=v0.1 "
        "candidate_implemented=true public=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
