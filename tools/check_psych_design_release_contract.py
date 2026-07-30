from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_ROOT = ROOT / "psych_design_companion/psych_design_release_contract_v0_1"
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


def fail(message: str) -> None:
    raise SystemExit(f"PYSTATSV1_PSYCH_DESIGN_RELEASE_CONTRACT_ERROR: {message}")


def read(name: str) -> dict:
    path = CONTRACT_ROOT / name
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"cannot read {path.relative_to(ROOT)}: {exc}")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    if not CONTRACT_ROOT.is_dir():
        fail("contract root is missing")
    names = {p.name for p in CONTRACT_ROOT.iterdir() if p.is_file()}
    if names != EXPECTED:
        fail(f"contract member set changed missing={sorted(EXPECTED-names)} extra={sorted(names-EXPECTED)}")

    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    if not re.search(r'^version = "0\.25\.2"$', pyproject, flags=re.MULTILINE):
        fail("baseline package version is not 0.25.2")
    if re.search(r'^psych-design\s*=', pyproject, flags=re.MULTILINE):
        fail("psych-design extra was implemented inside the contract-only unit")
    cli = (ROOT / "src/pystatsv1/cli.py").read_text(encoding="utf-8")
    if 'add_parser("psych-design"' in cli or "add_parser('psych-design'" in cli:
        fail("psych-design CLI was implemented inside the contract-only unit")

    release = read("COMPANION_RELEASE_CONTRACT.json")
    if release["baseline"] != {"main_commit":"6cd680812c7a149d4909eff4ddaf6e1679f6aba1","package_version":"0.25.2","repository":"PyStatsV1"}:
        fail("baseline identity changed")
    planned = release["planned_release"]
    required = {
        "package_version":"0.26.0",
        "release_tag":"v0.26.0",
        "optional_extra":"psych-design",
        "cli_namespace":"psych-design",
        "companion_version":"v0.1",
        "default_destination":"psychological_statistics_by_design_companion_v0_1",
        "asset_name":"psychological_statistics_by_design_companion_v0_1.zip",
    }
    for key,value in required.items():
        if planned.get(key) != value:
            fail(f"planned release field changed: {key}")
    life = release["lifecycle"]
    if life.get("contract_frozen") is not True:
        fail("contract is not frozen")
    for key in ("public_companion_released","pypi_release_authorized","portal_release_authorized","real_data_authorized","book_binding_authorized"):
        if life.get(key) is not False:
            fail(f"closed lifecycle gate changed: {key}")
    if release.get("study_ids") != [f"SWL-S{i:02d}" for i in range(1,11)]:
        fail("study ID registry is incomplete or out of order")
    if release.get("first_result_study") != "SWL-S02":
        fail("first-result study changed")

    commands = read("COMMAND_INTERFACE_CONTRACT.json")
    if commands.get("status") != "frozen_proposed_not_implemented_not_public":
        fail("command status may not imply implementation or release")
    if commands.get("package_install") != 'python -m pip install "pystatsv1[psych-design]==0.26.0"':
        fail("planned install command changed")
    if any(row.get("implemented") is not False for row in commands.get("commands", [])):
        fail("a proposed command is incorrectly marked implemented")
    expected_commands = {
        "pystatsv1 psych-design info",
        "pystatsv1 psych-design init",
        "pystatsv1 psych-design verify --dest .",
        "pystatsv1 psych-design list-studies",
        "pystatsv1 psych-design doctor --dest .",
    }
    if {row["command"] for row in commands["commands"]} != expected_commands:
        fail("command family changed")

    inventory = read("CURRENT_STUDY_ASSET_INVENTORY.json")["studies"]
    if {row["study_id"] for row in inventory} != {f"SWL-S{i:02d}" for i in range(1,11)}:
        fail("current study inventory is incomplete")
    for row in inventory:
        for key in ("dataset_path","design_contract_path","current_python_implementation","current_r_script","current_verification_script","python_result_receipt"):
            path = ROOT / row[key]
            if not path.is_file():
                fail(f"{row['study_id']} missing {key}: {row[key]}")
        for key in ("figure_sources","apa_source_maps","matched_limitations"):
            for rel in row[key]:
                if not (ROOT / rel).is_file():
                    fail(f"{row['study_id']} missing {key}: {rel}")
        if row.get("current_public_release") is not False or row.get("current_reader_command") is not None:
            fail(f"{row['study_id']} current release boundary changed")
        if not row.get("release_blockers"):
            fail(f"{row['study_id']} has no explicit release blockers")

    target = read("TARGET_STUDY_INDEX.json")
    if target.get("status") != "contract_not_implemented":
        fail("target study index incorrectly implies implementation")
    for row in target["studies"]:
        if row.get("status") != "target_contract_not_yet_implemented":
            fail(f"{row['study_id']} target status changed")
        if not row["reader_command"].endswith(row["study_id"]):
            fail(f"{row['study_id']} reader command does not bind the study ID")

    preservation = read("SOURCE_BATCH_PRESERVATION_MANIFEST.json")
    for batch in preservation["batches"]:
        actual_rows=[]
        for row in batch["files"]:
            path=ROOT/row["path"]
            if not path.is_file():
                fail(f"preserved source file missing: {row['path']}")
            if path.stat().st_size != row["bytes"] or digest(path) != row["sha256"]:
                fail(f"preserved source file drift: {row['path']}")
            actual_rows.append(f"{row['sha256']}  {row['path']}\n")
        tree=hashlib.sha256(''.join(actual_rows).encode()).hexdigest()
        if tree != batch["tree_sha256"] or len(actual_rows) != batch["file_count"]:
            fail(f"preserved source tree drift: {batch['batch_root']}")

    gaps = read("CROSS_REPOSITORY_GAP_MATRIX.json")["rows"]
    required_areas={"Source studies","CLI and PyPI extra","Visible per-study Python scripts","R verification","Study registry","Measurement maps","Reviewer packets","Licensing","Portal","Book interior","Clean reader proofs"}
    if {row["area"] for row in gaps} != required_areas:
        fail("cross-repository gap matrix is incomplete")

    license_contract=read("PUBLIC_ASSET_LICENSE_CONTRACT.json")
    if license_contract.get("current_repository_license") != "MIT" or not (ROOT/"LICENSE").is_file():
        fail("repository license boundary changed")
    if license_contract.get("real_data_included") is not False or license_contract.get("book_prose_included") is not False:
        fail("public asset exclusion boundary changed")

    anchors=read("CROSS_REPOSITORY_AUDIT_ANCHORS.json")["attachments"]
    if anchors["book"]["archive_commit"] != "ec14f859f4ce686ec0091f879382b5ac5bfaf5b3" or anchors["book"]["tests_passed"] != 676 or anchors["book"]["paperback_pages"] != 131:
        fail("book audit anchor changed")
    if anchors["portal"]["archive_commit"] != "b9c0f3a1a6dd4392e6e877d75b3c7d73aa249811":
        fail("portal audit anchor changed")

    print("PYSTATSV1_PSYCH_DESIGN_RELEASE_CONTRACT_VERIFY_OK studies=10 source_batches=3 planned_package=0.26.0 companion=v0.1")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
