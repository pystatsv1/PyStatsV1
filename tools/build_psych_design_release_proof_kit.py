#!/usr/bin/env python3
"""Freeze Ubuntu evidence and build the portable Drop-in 034 WSL proof kit."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import stat
import zipfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PROOF = ROOT / "release_proofs" / "psych_design_v0_1"
EVIDENCE = PROOF / "evidence"
RUNNER = ROOT / "tools" / "run_psych_design_clean_reader_proof.py"
WSL_RUNNER = PROOF / "run_wsl_release_proof.sh"
CONTRACT_PATH = PROOF / "RELEASE_PROOF_CONTRACT.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def zip_info(name: str, mode: int = 0o644) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
    info.create_system = 3
    info.external_attr = ((stat.S_IFREG | mode) & 0xFFFF) << 16
    info.compress_type = zipfile.ZIP_DEFLATED
    return info


def inspect_wheel(wheel: Path, contract: dict[str, Any]) -> dict[str, Any]:
    identity = contract["release_identity"]
    if wheel.name != identity["wheel_name"]:
        raise SystemExit("canonical wheel filename differs from the contract")
    if sha256(wheel) != identity["wheel_sha256"]:
        raise SystemExit("canonical wheel digest differs from the contract")
    if wheel.stat().st_size != identity["wheel_bytes"]:
        raise SystemExit("canonical wheel byte size differs from the contract")
    with zipfile.ZipFile(wheel) as archive:
        names = archive.namelist()
        asset_member = (
            "pystatsv1/assets/"
            "psychological_statistics_by_design_companion_v0_1.zip"
        )
        asset = archive.read(asset_member)
        metadata_name = next(name for name in names if name.endswith(".dist-info/METADATA"))
        metadata = archive.read(metadata_name).decode("utf-8")
        if "Version: 0.26.0\n" not in metadata:
            raise SystemExit("canonical wheel metadata does not declare version 0.26.0")
        if "Provides-Extra: psych-design\n" not in metadata:
            raise SystemExit("canonical wheel metadata does not expose psych-design")
    asset_hash = hashlib.sha256(asset).hexdigest()
    if asset_hash != identity["asset_sha256"]:
        raise SystemExit("canonical wheel contains the wrong companion asset")
    return {
        "wheel_name": wheel.name,
        "wheel_sha256": sha256(wheel),
        "wheel_bytes": wheel.stat().st_size,
        "wheel_member_count": len(names),
        "embedded_asset_member": asset_member,
        "embedded_asset_sha256": asset_hash,
        "embedded_asset_bytes": len(asset),
        "package_version": "0.26.0",
        "companion_version": "v0.1",
    }


def verify_rebuild(path: Path, contract: dict[str, Any]) -> dict[str, Any]:
    if not path.is_file():
        raise SystemExit(f"missing regenerated wheel: {path}")
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        metadata_name = next(name for name in names if name.endswith(".dist-info/METADATA"))
        metadata = archive.read(metadata_name).decode("utf-8")
        asset = archive.read(
            "pystatsv1/assets/psychological_statistics_by_design_companion_v0_1.zip"
        )
    if "Version: 0.26.0\n" not in metadata:
        raise SystemExit(f"regenerated wheel has the wrong version: {path}")
    if hashlib.sha256(asset).hexdigest() != contract["release_identity"]["asset_sha256"]:
        raise SystemExit(f"regenerated wheel has the wrong companion asset: {path}")
    return {
        "name": path.name,
        "sha256": sha256(path),
        "bytes": path.stat().st_size,
        "member_count": len(names),
        "asset_sha256": hashlib.sha256(asset).hexdigest(),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wheel", type=Path, required=True)
    parser.add_argument("--ubuntu-receipt", type=Path, required=True)
    parser.add_argument("--rebuild-first", type=Path, required=True)
    parser.add_argument("--rebuild-second", type=Path, required=True)
    parser.add_argument("--kit-zip", type=Path, required=True)
    args = parser.parse_args()

    contract = load(CONTRACT_PATH)
    wheel = args.wheel.expanduser().resolve()
    ubuntu_receipt = load(args.ubuntu_receipt.expanduser().resolve())
    if ubuntu_receipt.get("status") != "pass" or ubuntu_receipt.get("platform_role") != "ubuntu":
        raise SystemExit("Ubuntu receipt is not a passing native-Ubuntu proof")
    wheel_record = inspect_wheel(wheel, contract)
    if ubuntu_receipt["artifact_identity"]["wheel_sha256"] != wheel_record["wheel_sha256"]:
        raise SystemExit("Ubuntu proof did not use the canonical wheel")
    first = verify_rebuild(args.rebuild_first.expanduser().resolve(), contract)
    second = verify_rebuild(args.rebuild_second.expanduser().resolve(), contract)
    if first["sha256"] != second["sha256"]:
        raise SystemExit("two clean wheel regenerations are not byte-identical")

    wheel_identity = {
        "schema_version": "pystatsv1-psych-design-wheel-identity-v0.1",
        "candidate_commit": contract["baseline"]["candidate_commit"],
        "canonical_proof_wheel": wheel_record,
        "clean_regeneration": {
            "status": "pass",
            "build_1": first,
            "build_2": second,
            "byte_identical": True,
            "canonical_wheel_may_differ_from_local_regeneration": (
                first["sha256"] != wheel_record["wheel_sha256"]
            ),
            "policy": (
                "Both reader environments use the exact canonical wheel. Local "
                "regeneration must be internally reproducible and contain the exact "
                "governed asset; public PyPI distribution hashes are recorded later."
            ),
        },
        "public_release_authorized": False,
    }
    asset_identity = {
        "schema_version": "pystatsv1-psych-design-asset-identity-v0.1",
        "candidate_commit": contract["baseline"]["candidate_commit"],
        "asset_path": contract["release_identity"]["asset_path"],
        "asset_sha256": contract["release_identity"]["asset_sha256"],
        "asset_bytes": contract["release_identity"]["asset_bytes"],
        "asset_manifest_sha256": contract["release_identity"]["asset_manifest_sha256"],
        "study_index_sha256": contract["release_identity"]["study_index_sha256"],
        "immutable_source_file_count": contract["release_identity"]["immutable_source_file_count"],
        "wheel_embedded_asset_sha256": wheel_record["embedded_asset_sha256"],
        "status": "pass",
    }
    readiness = {
        "schema_version": "pystatsv1-psych-design-release-readiness-v0.1",
        "candidate_commit": contract["baseline"]["candidate_commit"],
        "package_version": "0.26.0",
        "companion_version": "v0.1",
        "candidate_implementation_passed": True,
        "clean_ubuntu_proof_passed": True,
        "clean_wsl_proof_passed": False,
        "cross_platform_comparison_passed": False,
        "technical_release_ready": False,
        "pypi_release_authorized": False,
        "portal_release_authorized": False,
        "book_binding_authorized": False,
        "real_data_authorized": False,
        "status": "ubuntu_passed_wsl_pending",
    }
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(args.ubuntu_receipt, EVIDENCE / "PSYCH_DESIGN_UBUNTU_RELEASE_PROOF.json")
    write(EVIDENCE / "PSYCH_DESIGN_WHEEL_IDENTITY.json", wheel_identity)
    write(EVIDENCE / "PSYCH_DESIGN_ASSET_IDENTITY.json", asset_identity)
    write(EVIDENCE / "PSYCH_DESIGN_RELEASE_READINESS.json", readiness)

    kit_files: dict[str, tuple[bytes, int]] = {
        wheel.name: (wheel.read_bytes(), 0o644),
        "RELEASE_PROOF_CONTRACT.json": (CONTRACT_PATH.read_bytes(), 0o644),
        "PSYCH_DESIGN_UBUNTU_RELEASE_PROOF.json": (
            (EVIDENCE / "PSYCH_DESIGN_UBUNTU_RELEASE_PROOF.json").read_bytes(),
            0o644,
        ),
        "run_psych_design_clean_reader_proof.py": (RUNNER.read_bytes(), 0o755),
        "run_wsl_release_proof.sh": (WSL_RUNNER.read_bytes(), 0o755),
    }
    sums = []
    for name in sorted(kit_files):
        sums.append(f"{hashlib.sha256(kit_files[name][0]).hexdigest()}  {name}")
    kit_files["PYSTATSV1_DROPIN_034_WSL_KIT_SHA256SUMS.txt"] = (
        ("\n".join(sums) + "\n").encode("utf-8"),
        0o644,
    )
    kit_files["README_WSL_PROOF.txt"] = (
        (
            "PyStatsV1 Drop-in 034 WSL proof kit\n\n"
            "Unpack this ZIP inside the WSL Linux home, not under /mnt/c.\n"
            "Then run: bash run_wsl_release_proof.sh\n"
            "The script creates a result ZIP in $HOME/Downloads.\n"
            "No PyPI publication, portal edit, book edit, or real-data action occurs.\n"
        ).encode("utf-8"),
        0o644,
    )
    args.kit_zip.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(
        args.kit_zip, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as archive:
        for name in sorted(kit_files):
            data, mode = kit_files[name]
            archive.writestr(zip_info(name, mode), data)
    print(
        "PYSTATSV1_DROPIN_034_WSL_KIT_BUILT "
        f"wheel={wheel_record['wheel_sha256']} kit={args.kit_zip} "
        f"kit_sha256={sha256(args.kit_zip)}"
    )


if __name__ == "__main__":
    main()
