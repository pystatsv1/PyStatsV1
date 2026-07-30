#!/usr/bin/env python3
"""Verify the Drop-in 034 source freeze and staged/complete proof evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import zipfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PROOF = ROOT / "release_proofs" / "psych_design_v0_1"
EVIDENCE = PROOF / "evidence"
CONTRACT = PROOF / "RELEASE_PROOF_CONTRACT.json"
FREEZE = PROOF / "CANDIDATE_FREEZE.json"
SOURCE = ROOT / "psych_design_companion" / "psychological_statistics_by_design_companion_v0_1"
ASSET = ROOT / "src" / "pystatsv1" / "assets" / "psychological_statistics_by_design_companion_v0_1.zip"
EXPECTED_STUDIES = [f"SWL-S{number:02d}" for number in range(1, 11)]


def fail(message: str) -> None:
    raise SystemExit(f"PYSTATSV1_PSYCH_DESIGN_RELEASE_PROOF_ERROR: {message}")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"invalid JSON {path.relative_to(ROOT)}: {exc}")


def verify_source_freeze(contract: dict[str, Any], freeze: dict[str, Any]) -> None:
    if contract.get("schema_version") != "pystatsv1-psych-design-release-proof-contract-v0.1":
        fail("release-proof contract schema changed")
    if contract.get("dropin") != "034":
        fail("release-proof contract is not Drop-in 034")
    baseline = contract["baseline"]
    if baseline["candidate_commit"] != "58d92f85b865cb657bf49c731fefc381970c8bda":
        fail("candidate commit changed")
    if baseline["candidate_tag"] != "psych-design-companion-v0-1-candidate":
        fail("candidate tag changed")
    if baseline["reserved_final_release_tag"] != "v0.26.0":
        fail("reserved final release tag changed")
    identity = contract["release_identity"]
    if identity["package_version"] != "0.26.0" or identity["companion_version"] != "v0.1":
        fail("release identity changed")
    if identity["wheel_sha256"] != "62a5c26577867f22c7bbf15dcf4253da749fe703fcec42ffc19b72454af8fa05":
        fail("canonical wheel identity changed")
    if identity["asset_sha256"] != sha256(ASSET):
        fail("candidate companion asset changed")
    if identity["asset_bytes"] != ASSET.stat().st_size:
        fail("candidate companion asset byte size changed")
    if freeze["asset_sha256"] != identity["asset_sha256"]:
        fail("candidate freeze and release contract disagree")

    with zipfile.ZipFile(ASSET) as archive:
        manifest_bytes = archive.read("COMPANION_MANIFEST.json")
        index_bytes = archive.read("STUDY_INDEX.json")
        manifest = json.loads(manifest_bytes)
        if hashlib.sha256(manifest_bytes).hexdigest() != identity["asset_manifest_sha256"]:
            fail("asset manifest identity changed")
        if hashlib.sha256(index_bytes).hexdigest() != identity["study_index_sha256"]:
            fail("study index identity changed")
        if len(manifest.get("files", [])) != 151:
            fail("candidate immutable source-file count changed")
        if manifest.get("study_ids") != EXPECTED_STUDIES:
            fail("candidate asset study IDs changed")
        for row in manifest["files"]:
            path = SOURCE / row["path"]
            if not path.is_file():
                fail(f"candidate source file missing: {row['path']}")
            if sha256(path) != row["sha256"]:
                fail(f"candidate source drift: {row['path']}")
            if hashlib.sha256(archive.read(row["path"])).hexdigest() != row["sha256"]:
                fail(f"candidate asset member drift: {row['path']}")
    if (SOURCE / "outputs").exists():
        fail("generated companion outputs must not remain in the repository")

    lifecycle = contract["lifecycle"]
    for key in (
        "public_pypi_release_authorized",
        "portal_release_authorized",
        "book_binding_authorized",
        "real_data_authorized",
    ):
        if lifecycle.get(key) is not False:
            fail(f"release contract opens closed gate: {key}")
    if contract["publication_workflow_policy"]["candidate_tag_may_not_publish"] is not True:
        fail("candidate-tag publication prohibition changed")


def verify_publication_workflow() -> None:
    path = ROOT / ".github" / "workflows" / "pypi-publish.yml"
    text = path.read_text(encoding="utf-8")
    required = (
        "workflow_dispatch:",
        "git cat-file -t",
        'if [ "$object_type" != "tag" ]',
        "tagged_commit=",
        "checked_out_commit=",
        "python tools/check_release_tag.py",
        "pypa/gh-action-pypi-publish@release/v1",
    )
    for token in required:
        if token not in text:
            fail(f"trusted-publisher workflow lost release gate: {token}")
    if "psych-design-companion-v0-1-candidate" in text:
        fail("candidate tag is wired into the publication workflow")


def verify_git_state() -> None:
    if not (ROOT / ".git").exists():
        return
    tags = subprocess.check_output(["git", "tag", "--list"], cwd=ROOT, text=True).splitlines()
    if "v0.26.0" in tags:
        fail("v0.26.0 must remain absent until explicit release authorization")
    if "psych-design-companion-v0-1-candidate" not in tags:
        fail("candidate tag is missing")
    candidate = subprocess.check_output(
        ["git", "rev-parse", "psych-design-companion-v0-1-candidate^{commit}"],
        cwd=ROOT,
        text=True,
    ).strip()
    if candidate != "58d92f85b865cb657bf49c731fefc381970c8bda":
        fail("candidate tag does not resolve to the frozen candidate commit")


def verify_receipt(path: Path, role: str, contract: dict[str, Any]) -> dict[str, Any]:
    receipt = load(path)
    if receipt.get("schema_version") != "pystatsv1-psych-design-clean-reader-proof-v0.1":
        fail(f"{role} receipt schema changed")
    if receipt.get("status") != "pass" or receipt.get("platform_role") != role:
        fail(f"{role} receipt is not a passing {role} proof")
    if receipt.get("candidate_commit") != contract["baseline"]["candidate_commit"]:
        fail(f"{role} receipt candidate commit changed")
    identity = receipt.get("artifact_identity", {})
    expected = contract["release_identity"]
    for key in ("wheel_sha256", "wheel_bytes", "asset_sha256", "asset_bytes"):
        if identity.get(key) != expected[key]:
            fail(f"{role} receipt artifact identity mismatch: {key}")
    if identity.get("source_manifest_sha256") != expected["asset_manifest_sha256"]:
        fail(f"{role} receipt source manifest mismatch")
    if identity.get("study_index_sha256") != expected["study_index_sha256"]:
        fail(f"{role} receipt study index mismatch")
    if identity.get("source_file_count") != 151 or identity.get("source_manifest_status") != "pass":
        fail(f"{role} receipt source verification is incomplete")
    if sorted(receipt.get("study_evidence", {})) != EXPECTED_STUDIES:
        fail(f"{role} receipt does not cover all studies")
    if not all(receipt.get("command_markers", {}).values()):
        fail(f"{role} receipt missed a required marker")
    for study in EXPECTED_STUDIES:
        row = receipt["study_evidence"][study]
        if row.get("verification_status") != "pass":
            fail(f"{role} receipt has failed verification for {study}")
        if row.get("reviewer_packet_file_count") != 12:
            fail(f"{role} reviewer packet is incomplete for {study}")
    return receipt


def verify_ubuntu_phase(contract: dict[str, Any]) -> None:
    ubuntu = verify_receipt(
        EVIDENCE / "PSYCH_DESIGN_UBUNTU_RELEASE_PROOF.json", "ubuntu", contract
    )
    wheel = load(EVIDENCE / "PSYCH_DESIGN_WHEEL_IDENTITY.json")
    asset = load(EVIDENCE / "PSYCH_DESIGN_ASSET_IDENTITY.json")
    readiness = load(EVIDENCE / "PSYCH_DESIGN_RELEASE_READINESS.json")
    if wheel.get("canonical_proof_wheel", {}).get("wheel_sha256") != contract["release_identity"]["wheel_sha256"]:
        fail("wheel identity receipt differs from the contract")
    regeneration = wheel.get("clean_regeneration", {})
    if regeneration.get("status") != "pass" or regeneration.get("byte_identical") is not True:
        fail("clean wheel regeneration did not pass")
    if asset.get("status") != "pass" or asset.get("asset_sha256") != contract["release_identity"]["asset_sha256"]:
        fail("asset identity receipt did not pass")
    if readiness.get("clean_ubuntu_proof_passed") is not True:
        fail("Ubuntu readiness state is not passed")
    if readiness.get("clean_wsl_proof_passed") is not False:
        fail("Ubuntu stage must retain WSL pending")
    if readiness.get("technical_release_ready") is not False:
        fail("Ubuntu stage may not declare technical release readiness")
    if ubuntu["workspace_policy"].get("is_wsl") is not False:
        fail("Ubuntu receipt was not produced on native Ubuntu")


def verify_complete_phase(contract: dict[str, Any]) -> None:
    verify_ubuntu_phase(contract)
    wsl = verify_receipt(
        EVIDENCE / "PSYCH_DESIGN_WSL_RELEASE_PROOF.json", "wsl", contract
    )
    workspace = wsl.get("workspace_policy", {})
    if workspace.get("is_wsl") is not True:
        fail("WSL receipt was not produced inside WSL")
    if workspace.get("is_wsl2") is not True:
        fail("WSL receipt was not produced inside WSL2")
    if workspace.get("workspace_under_linux_home") is not True:
        fail("WSL proof workspace was not inside the Linux home")
    if workspace.get("absolute_workspace_path_recorded") is not False:
        fail("WSL receipt records an absolute workspace path")
    facts = wsl.get("system_facts", {})
    for key in (
        "windows_version",
        "wsl_version",
        "ubuntu_release",
        "kernel",
        "python_version",
        "pip_version",
        "r_version",
        "rscript_version",
        "r_session_info",
        "nlme_version",
    ):
        value = facts.get(key)
        if value in (None, ""):
            fail(f"WSL receipt did not record required system fact: {key}")
        if isinstance(value, str) and value.lower().startswith("unavailable"):
            fail(f"WSL receipt could not collect required system fact: {key}")
    comparison = load(EVIDENCE / "PSYCH_DESIGN_CROSS_PLATFORM_COMPARISON.json")
    readiness = load(EVIDENCE / "PSYCH_DESIGN_RELEASE_READINESS.json")
    if comparison.get("status") != "pass" or comparison.get("failed_exact_checks") != []:
        fail("cross-platform comparison did not pass")
    if comparison.get("png_renderer_comparison", {}).get("png_byte_identity_required") is not False:
        fail("comparison incorrectly requires PNG byte identity")
    if readiness.get("technical_release_ready") is not True:
        fail("complete proof did not declare technical release readiness")
    for key in (
        "pypi_release_authorized",
        "portal_release_authorized",
        "book_binding_authorized",
        "real_data_authorized",
    ):
        if readiness.get(key) is not False:
            fail(f"complete proof opens closed gate: {key}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", choices=("source", "ubuntu", "complete"), default="source")
    args = parser.parse_args()
    contract = load(CONTRACT)
    freeze = load(FREEZE)
    verify_source_freeze(contract, freeze)
    verify_publication_workflow()
    verify_git_state()
    required = (
        PROOF / "README.md",
        PROOF / "run_wsl_release_proof.sh",
        ROOT / "tools" / "run_psych_design_clean_reader_proof.py",
        ROOT / "tools" / "build_psych_design_release_proof_kit.py",
        ROOT / "tools" / "compare_psych_design_release_proofs.py",
        ROOT / "docs" / "PYSTATSV1_DROPIN_034_PSYCH_DESIGN_CLEAN_READER_RELEASE_PROOF.md",
    )
    for path in required:
        if not path.is_file():
            fail(f"required Drop-in 034 path is missing: {path.relative_to(ROOT)}")
    if args.phase in {"ubuntu", "complete"}:
        verify_ubuntu_phase(contract)
    if args.phase == "complete":
        verify_complete_phase(contract)
    print(
        "PYSTATSV1_PSYCH_DESIGN_RELEASE_PROOF_VERIFY_OK "
        f"phase={args.phase} candidate=58d92f85 package=0.26.0 companion=v0.1 public=false"
    )


if __name__ == "__main__":
    main()
