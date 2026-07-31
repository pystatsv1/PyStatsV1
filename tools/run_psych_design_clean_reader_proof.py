#!/usr/bin/env python3
"""Run the clean installed-wheel psych-design proof and emit one bounded receipt."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import Any

DEFAULT_COMPANION = "psychological_statistics_by_design_companion_v0_1"
ASSET_MEMBER = "pystatsv1/assets/psychological_statistics_by_design_companion_v0_1.zip"
EXPECTED_STUDIES = [f"SWL-S{number:02d}" for number in range(1, 11)]
EXPECTED_MARKERS = (
    "PYSTATSV1_PSYCH_DESIGN_VERIFY_OK",
    "PYSTATSV1_PSYCH_DESIGN_DOCTOR_OK",
    "PYSTATSV1_PSYCH_DESIGN_FIRST_RESULT_OK",
    "PYSTATSV1_PSYCH_DESIGN_ALL_PYTHON_OK",
    "PYSTATSV1_PSYCH_DESIGN_ALL_R_OK",
    "PYSTATSV1_PSYCH_DESIGN_ALL_VERIFICATION_OK",
    "PYSTATSV1_PSYCH_DESIGN_COMPANION_ALL_OK",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def canonical_number(value: Any) -> Any:
    if isinstance(value, bool) or value is None or isinstance(value, str):
        return value
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return format(value, ".12g")
    if isinstance(value, list):
        return [canonical_number(item) for item in value]
    if isinstance(value, dict):
        return {key: canonical_number(value[key]) for key in sorted(value)}
    return value


def run(
    command: list[str],
    *,
    cwd: Path,
    env: dict[str, str],
    logs: Path,
    name: str,
    marker: str | None = None,
) -> str:
    completed = subprocess.run(
        command,
        cwd=cwd,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    output = completed.stdout
    (logs / f"{name}.log").write_text(output, encoding="utf-8", newline="\n")
    if completed.returncode != 0:
        raise SystemExit(
            f"clean-reader command failed ({name}): {' '.join(command)}\n{output}"
        )
    if marker is not None and marker not in output:
        raise SystemExit(f"clean-reader command {name} missed marker {marker!r}")
    return output


def probe(command: list[str]) -> str:
    try:
        completed = subprocess.run(
            command,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
    except OSError as exc:
        return f"unavailable: {exc}"
    output = completed.stdout.replace("\x00", "").strip()
    if completed.returncode != 0:
        return f"unavailable (exit {completed.returncode}): {output}"
    return output


def os_release() -> dict[str, str]:
    path = Path("/etc/os-release")
    result: dict[str, str] = {}
    if path.is_file():
        for line in path.read_text(encoding="utf-8").splitlines():
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            result[key] = value.strip().strip('"')
    return result


def assert_platform(role: str, workspace: Path) -> dict[str, Any]:
    release_lower = platform.release().lower()
    proc_version = Path("/proc/version").read_text(encoding="utf-8", errors="replace")
    proc_lower = proc_version.lower()
    is_wsl = "microsoft" in release_lower or "microsoft" in proc_lower
    is_wsl2 = is_wsl and (
        "wsl2" in release_lower
        or "microsoft-standard" in release_lower
        or "wsl2" in proc_lower
        or "microsoft-standard" in proc_lower
    )
    if role == "wsl" and not is_wsl2:
        raise SystemExit("the WSL proof runner must execute inside Windows 11 WSL2")
    if role == "ubuntu" and is_wsl:
        raise SystemExit("the native Ubuntu proof may not be substituted by WSL")

    resolved = workspace.expanduser().resolve()
    home = Path.home().resolve()
    try:
        relative_to_home = resolved.relative_to(home)
        under_home = True
    except ValueError:
        relative_to_home = None
        under_home = False
    if not under_home:
        raise SystemExit("clean-reader proof workspace must be inside the Linux home")
    if role == "wsl" and str(resolved).startswith("/mnt/"):
        raise SystemExit("WSL proof workspace must be inside the Linux home, not /mnt")

    if sys.version_info[:2] != (3, 10):
        raise SystemExit(
            f"clean-reader proof requires CPython 3.10.x, found {platform.python_version()}"
        )
    for required in ("make", "R", "Rscript"):
        if shutil.which(required) is None:
            raise SystemExit(f"{required} is required for the complete proof")
    if role == "wsl":
        for required in ("cmd.exe", "wsl.exe"):
            if shutil.which(required) is None:
                raise SystemExit(
                    f"{required} is required to record the Windows 11 WSL2 environment"
                )
    return {
        "role": role,
        "is_wsl": is_wsl,
        "is_wsl2": is_wsl2,
        "workspace_under_linux_home": under_home,
        "workspace_relative_to_home": str(relative_to_home),
        "absolute_workspace_path_recorded": False,
    }


def read_csv_metrics(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        rows = csv.DictReader(handle)
        if rows.fieldnames != ["metric", "value"]:
            raise SystemExit(f"unexpected R result columns in {path}")
        for row in rows:
            name = str(row["metric"]).strip()
            result[name] = format(float(row["value"]), ".12g")
    return {key: result[key] for key in sorted(result)}


def source_bindings(companion: Path, index: dict[str, Any]) -> dict[str, Any]:
    records: dict[str, Any] = {}
    for row in index["studies"]:
        study = row["study_id"]
        records[study] = {
            "dataset": {row["dataset_path"]: sha256(companion / row["dataset_path"])},
            "design": {
                row["design_contract_path"]: sha256(
                    companion / row["design_contract_path"]
                )
            },
            "measurement": {
                row["measurement_map_path"]: sha256(
                    companion / row["measurement_map_path"]
                )
            },
            "apa_source_maps": {
                rel: sha256(companion / rel) for rel in sorted(row["apa_source_maps"])
            },
            "matched_limitations": {
                rel: sha256(companion / rel)
                for rel in sorted(row["matched_limitations"])
            },
            "figure_specs": {
                rel: sha256(companion / rel) for rel in sorted(row["figure_specs"])
            },
        }
    return records


def figure_evidence(output: Path) -> dict[str, Any]:
    from PIL import Image

    manifest_path = output / "figures" / "FIGURE_MANIFEST.json"
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    figures = []
    for row in payload["figures"]:
        image_path = output / "figures" / row["output"]
        with Image.open(image_path) as image:
            width, height = image.size
        figures.append(
            {
                "output": row["output"],
                "role": row["role"],
                "dpi": row["dpi"],
                "grayscale": row["grayscale"],
                "pixel_dimensions": [width, height],
                "png_sha256": sha256(image_path),
            }
        )
    return {
        "manifest_semantics": {
            "schema_version": payload["schema_version"],
            "study_id": payload["study_id"],
            "synthetic_only": payload["synthetic_only"],
            "figures": [
                {key: row[key] for key in row if key != "png_sha256"} for row in figures
            ],
        },
        "png_hashes": {row["output"]: row["png_sha256"] for row in figures},
    }


def collect_study_evidence(companion: Path, index: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for row in index["studies"]:
        study = row["study_id"]
        slug = study.lower().replace("-", "_")
        output = companion / "outputs" / slug
        python_path = output / "python_result.json"
        r_path = output / "r_result.csv"
        verification_path = output / "verification_receipt.json"
        packet = output / "reviewer_packet"
        packet_manifest = json.loads((packet / "MANIFEST.json").read_text(encoding="utf-8"))
        python_payload = json.loads(python_path.read_text(encoding="utf-8"))
        verification = json.loads(verification_path.read_text(encoding="utf-8"))
        result[study] = {
            "verification_category": row["verification_category"],
            "python_result_sha256": sha256(python_path),
            "python_reported_fields": canonical_number(python_payload["reported_fields"]),
            "r_result_sha256": sha256(r_path),
            "r_metrics": read_csv_metrics(r_path),
            "verification_receipt_sha256": sha256(verification_path),
            "verification_status": verification["status"],
            "verification_comparisons": canonical_number(
                verification["comparisons"]
            ),
            "v4_documented_not_equal_fields": verification.get(
                "v4_documented_not_equal_fields", []
            ),
            "reviewer_packet_membership": sorted(
                item["path"] for item in packet_manifest["files"]
            ),
            "reviewer_packet_file_count": packet_manifest["file_count"],
            "reviewer_packet_source_hashes": {
                item["path"]: item["sha256"]
                for item in packet_manifest["files"]
                if item["path"] not in {"FIGURE_MANIFEST.json"}
            },
            "apa_runtime_binding_sha256": sha256(output / "apa_source_map.json"),
            "matched_limitation_runtime_sha256": sha256(
                output / "matched_limitation.md"
            ),
            "figures": figure_evidence(output),
        }
    return result


def installed_identity(venv_python: Path) -> dict[str, Any]:
    code = """
import hashlib, json
from importlib import metadata, resources
name='psychological_statistics_by_design_companion_v0_1.zip'
asset=resources.files('pystatsv1.assets')/name
with resources.as_file(asset) as path:
    data=path.read_bytes()
print(json.dumps({'package_version': metadata.version('pystatsv1'), 'asset_sha256': hashlib.sha256(data).hexdigest(), 'asset_bytes': len(data)}))
"""
    completed = subprocess.run(
        [str(venv_python), "-c", code],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        raise SystemExit(completed.stdout + completed.stderr)
    return json.loads(completed.stdout)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--platform", choices=("ubuntu", "wsl"), required=True)
    parser.add_argument("--wheel", type=Path, required=True)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    args = parser.parse_args()

    contract = json.loads(args.contract.read_text(encoding="utf-8"))
    identity = contract["release_identity"]
    wheel = args.wheel.expanduser().resolve()
    workspace = args.workspace.expanduser().resolve()
    receipt = args.receipt.expanduser().resolve()
    if workspace.exists():
        raise SystemExit(f"refusing to reuse clean-reader workspace: {workspace}")
    if receipt.exists():
        raise SystemExit(f"refusing to overwrite release-proof receipt: {receipt}")
    if not wheel.is_file():
        raise SystemExit(f"canonical wheel not found: {wheel}")
    if wheel.name != identity["wheel_name"]:
        raise SystemExit("canonical wheel filename does not match the release contract")
    if sha256(wheel) != identity["wheel_sha256"]:
        raise SystemExit("canonical wheel SHA-256 does not match the release contract")
    if wheel.stat().st_size != identity["wheel_bytes"]:
        raise SystemExit("canonical wheel byte size does not match the release contract")
    with zipfile.ZipFile(wheel) as archive:
        asset_data = archive.read(ASSET_MEMBER)
    if hashlib.sha256(asset_data).hexdigest() != identity["asset_sha256"]:
        raise SystemExit("wheel does not contain the exact governed companion asset")

    platform_facts = assert_platform(args.platform, workspace)
    workspace.mkdir(parents=True)
    logs = workspace / "logs"
    logs.mkdir()
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONHASHSEED"] = "0"

    run(
        [sys.executable, "-m", "venv", ".venv"],
        cwd=workspace,
        env=env,
        logs=logs,
        name="01_create_venv",
    )
    venv_python = workspace / ".venv" / "bin" / "python"
    venv_cli = workspace / ".venv" / "bin" / "pystatsv1"
    proof_env = env.copy()
    proof_env["PATH"] = f"{workspace / '.venv' / 'bin'}:{proof_env.get('PATH', '')}"

    run(
        [str(venv_python), "-m", "pip", "install", "--upgrade", "pip"],
        cwd=workspace,
        env=proof_env,
        logs=logs,
        name="02_upgrade_pip",
    )
    run(
        [str(venv_python), "-m", "pip", "install", f"{wheel}[psych-design]"],
        cwd=workspace,
        env=proof_env,
        logs=logs,
        name="03_install_wheel",
    )
    info_output = run(
        [str(venv_cli), "psych-design", "info"],
        cwd=workspace,
        env=proof_env,
        logs=logs,
        name="04_info",
        marker="Companion version: v0.1",
    )
    companion = workspace / DEFAULT_COMPANION
    init_output = run(
        [str(venv_cli), "psych-design", "init", "--dest", str(companion)],
        cwd=workspace,
        env=proof_env,
        logs=logs,
        name="05_init",
        marker="Verified source files: 151",
    )
    verify_before = run(
        [str(venv_cli), "psych-design", "verify", "--dest", str(companion)],
        cwd=workspace,
        env=proof_env,
        logs=logs,
        name="06_verify_before",
        marker="PYSTATSV1_PSYCH_DESIGN_VERIFY_OK",
    )
    run(
        [
            str(venv_python),
            "-m",
            "pip",
            "install",
            "-r",
            str(companion / "requirements-psych-design-companion.txt"),
        ],
        cwd=companion,
        env=proof_env,
        logs=logs,
        name="07_install_companion_requirements",
    )
    doctor_output = run(
        [str(venv_cli), "psych-design", "doctor", "--dest", str(companion)],
        cwd=companion,
        env=proof_env,
        logs=logs,
        name="08_doctor",
        marker="PYSTATSV1_PSYCH_DESIGN_DOCTOR_OK",
    )
    first_result = run(
        ["make", "first-result"],
        cwd=companion,
        env=proof_env,
        logs=logs,
        name="09_first_result",
        marker="PYSTATSV1_PSYCH_DESIGN_FIRST_RESULT_OK",
    )
    all_output = run(
        ["make", "all"],
        cwd=companion,
        env=proof_env,
        logs=logs,
        name="10_make_all",
        marker="PYSTATSV1_PSYCH_DESIGN_COMPANION_ALL_OK",
    )
    verify_after = run(
        [str(venv_cli), "psych-design", "verify", "--dest", str(companion)],
        cwd=companion,
        env=proof_env,
        logs=logs,
        name="11_verify_after",
        marker="PYSTATSV1_PSYCH_DESIGN_VERIFY_OK",
    )

    combined = "\n".join(
        (info_output, init_output, verify_before, doctor_output, first_result, all_output, verify_after)
    )
    marker_status = {marker: marker in combined for marker in EXPECTED_MARKERS}
    if not all(marker_status.values()):
        missing = [marker for marker, present in marker_status.items() if not present]
        raise SystemExit("clean-reader proof missed markers: " + ", ".join(missing))

    manifest_path = companion / "COMPANION_MANIFEST.json"
    index_path = companion / "STUDY_INDEX.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    index = json.loads(index_path.read_text(encoding="utf-8"))
    if [row["study_id"] for row in index["studies"]] != EXPECTED_STUDIES:
        raise SystemExit("installed companion study registry is incomplete")
    installed = installed_identity(venv_python)
    if installed["package_version"] != identity["package_version"]:
        raise SystemExit("installed package version differs from the release contract")
    if installed["asset_sha256"] != identity["asset_sha256"]:
        raise SystemExit("installed package asset differs from the release contract")

    system_facts = {
        "platform_role": args.platform,
        "platform": platform.platform(),
        "kernel": platform.release(),
        "uname": probe(["uname", "-a"]),
        "ubuntu_release": os_release(),
        "python_version": probe([str(venv_python), "--version"]),
        "python_executable": ".venv/bin/python",
        "pip_version": probe([str(venv_python), "-m", "pip", "--version"]),
        "r_version": probe(["R", "--version"]),
        "rscript_version": probe(["Rscript", "--version"]),
        "r_session_info": probe(["Rscript", "-e", "sessionInfo()"]),
        "nlme_version": probe(["Rscript", "-e", 'cat(as.character(packageVersion("nlme")))']),
        "windows_version": (
            probe(["cmd.exe", "/c", "ver"]) if args.platform == "wsl" else "not_applicable"
        ),
        "wsl_version": (
            probe(["wsl.exe", "--version"]) if args.platform == "wsl" else "not_applicable"
        ),
    }

    receipt_payload = {
        "schema_version": "pystatsv1-psych-design-clean-reader-proof-v0.1",
        "status": "pass",
        "platform_role": args.platform,
        "candidate_commit": contract["baseline"]["candidate_commit"],
        "candidate_tag": contract["baseline"]["candidate_tag"],
        "package_version": installed["package_version"],
        "companion_version": manifest["companion_version"],
        "synthetic_only": True,
        "real_data_authorized": False,
        "workspace_policy": platform_facts,
        "system_facts": system_facts,
        "artifact_identity": {
            "wheel_name": wheel.name,
            "wheel_sha256": sha256(wheel),
            "wheel_bytes": wheel.stat().st_size,
            "asset_sha256": installed["asset_sha256"],
            "asset_bytes": installed["asset_bytes"],
            "source_manifest_sha256": sha256(manifest_path),
            "study_index_sha256": sha256(index_path),
            "source_file_count": len(manifest["files"]),
            "source_manifest_status": "pass",
        },
        "command_markers": marker_status,
        "source_bindings": source_bindings(companion, index),
        "study_evidence": collect_study_evidence(companion, index),
        "publication_gates": {
            "pypi_release_authorized": False,
            "portal_release_authorized": False,
            "book_binding_authorized": False,
            "real_data_authorized": False,
        },
        "log_files": {
            path.name: sha256(path) for path in sorted(logs.glob("*.log"))
        },
    }
    write_json(receipt, receipt_payload)
    print(
        "PYSTATSV1_PSYCH_DESIGN_CLEAN_READER_PROOF_OK "
        f"platform={args.platform} studies=10 wheel={receipt_payload['artifact_identity']['wheel_sha256']} "
        f"receipt={receipt}"
    )


if __name__ == "__main__":
    main()
