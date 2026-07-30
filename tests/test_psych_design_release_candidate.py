from __future__ import annotations

import csv
import hashlib
import json
import stat
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

from pystatsv1.psych_design import (
    ASSET_NAME,
    CURRENT_COMPANION_VERSION,
    EXPECTED_PACKAGE_VERSION,
    MANIFEST_NAME,
    _read_manifest_from_zip,
    _validate_zip_members,
    initialize_psych_design,
    packaged_psych_design_info,
    packaged_study_index,
    psych_design_doctor,
    verify_psych_design_directory,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (
    ROOT
    / "psych_design_companion"
    / "psychological_statistics_by_design_companion_v0_1"
)
ASSET = ROOT / "src" / "pystatsv1" / "assets" / ASSET_NAME
BUILDER = ROOT / "tools" / "build_psych_design_companion_asset.py"
EXPECTED_STUDIES = [f"SWL-S{number:02d}" for number in range(1, 11)]


def run(*command: str, cwd: Path = ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(command),
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_psych_design_registry_is_complete_and_has_no_placeholders() -> None:
    index = json.loads((SOURCE / "STUDY_INDEX.json").read_text(encoding="utf-8"))
    assert index["status"] == "release_candidate_implemented_not_public"
    assert index["companion_version"] == CURRENT_COMPANION_VERSION
    assert index["package_release_candidate"] == EXPECTED_PACKAGE_VERSION
    assert index["synthetic_only"] is True
    assert index["real_data_authorized"] is False
    assert [row["study_id"] for row in index["studies"]] == EXPECTED_STUDIES
    assert len({row["python_script"] for row in index["studies"]}) == 10
    serialized = json.dumps(index).lower()
    for placeholder in (
        "to be copied from the governed",
        "target_contract_not_yet_implemented",
        "contract_not_implemented",
    ):
        assert placeholder not in serialized
    for row in index["studies"]:
        for key in (
            "dataset_path",
            "design_contract_path",
            "measurement_map_path",
            "python_script",
            "r_launcher",
            "r_script",
            "verification_script",
            "reference_python_result",
        ):
            assert (SOURCE / row[key]).is_file(), (row["study_id"], key)
        assert row["reader_command"] == f"make study STUDY={row['study_id']}"
        assert row["verification_command"] == (
            f"make verify-study STUDY={row['study_id']}"
        )
        assert row["packet_command"] == f"make packet STUDY={row['study_id']}"


def test_psych_design_asset_is_exactly_reproducible(tmp_path: Path) -> None:
    first = tmp_path / "first.zip"
    second = tmp_path / "second.zip"
    for destination in (first, second):
        completed = run(
            sys.executable,
            str(BUILDER),
            "--dest",
            str(destination),
        )
        assert completed.returncode == 0, completed.stdout + completed.stderr
    assert sha256(first) == sha256(second) == sha256(ASSET)


def test_packaged_psych_design_manifest_and_index_are_bound() -> None:
    manifest = packaged_psych_design_info()
    index = packaged_study_index()
    assert manifest["companion_version"] == "v0.1"
    assert manifest["package_version"] == "0.26.0"
    assert manifest["release_status"] == "release_candidate_not_public"
    assert manifest["synthetic_data_only"] is True
    assert manifest["real_data_authorized"] is False
    assert manifest["study_ids"] == EXPECTED_STUDIES
    assert manifest["first_result_study"] == "SWL-S02"
    assert [row["study_id"] for row in index["studies"]] == EXPECTED_STUDIES
    assert len(manifest["files"]) >= 140


def test_psych_design_init_verify_and_generated_output_boundary(tmp_path: Path) -> None:
    destination = tmp_path / "companion"
    result = initialize_psych_design(destination)
    assert result.companion_version == "v0.1"
    assert result.file_count >= 140
    assert (destination / "STUDY_INDEX.json").is_file()
    before = verify_psych_design_directory(destination)
    generated = destination / "outputs" / "reader-note.txt"
    generated.parent.mkdir(parents=True)
    generated.write_text("reader-generated output\n", encoding="utf-8")
    after = verify_psych_design_directory(destination)
    assert before.file_count == after.file_count


def test_psych_design_init_refuses_existing_destination(tmp_path: Path) -> None:
    destination = tmp_path / "existing"
    destination.mkdir()
    with pytest.raises(RuntimeError, match="refusing to overwrite"):
        initialize_psych_design(destination)


def test_psych_design_verify_detects_source_tampering(tmp_path: Path) -> None:
    destination = tmp_path / "companion"
    initialize_psych_design(destination)
    readme = destination / "README.md"
    readme.write_text(
        readme.read_text(encoding="utf-8") + "\ntampered\n",
        encoding="utf-8",
    )
    with pytest.raises(RuntimeError, match="hash mismatch"):
        verify_psych_design_directory(destination)


def test_psych_design_doctor_reports_bounded_roles(tmp_path: Path) -> None:
    destination = tmp_path / "companion"
    initialize_psych_design(destination)
    payload = psych_design_doctor(destination)
    assert payload["companion_version"] == "v0.1"
    assert payload["source_manifest_status"] == "pass"
    assert payload["synthetic_data_only"] is True
    assert payload["real_data_authorized"] is False
    assert "method" not in payload
    assert "Ubuntu/WSL" in payload["supported_platform_status"]


def test_psych_design_cli_info_list_init_verify_and_doctor(tmp_path: Path) -> None:
    destination = tmp_path / "cli-companion"
    cases = (
        (["psych-design", "info"], "Companion version: v0.1"),
        (["psych-design", "list-studies"], "SWL-S10"),
        (
            ["psych-design", "init", "--dest", str(destination)],
            "Verified source files:",
        ),
        (
            ["psych-design", "verify", "--dest", str(destination)],
            "PYSTATSV1_PSYCH_DESIGN_VERIFY_OK",
        ),
        (
            ["psych-design", "doctor", "--dest", str(destination)],
            "PYSTATSV1_PSYCH_DESIGN_DOCTOR_OK",
        ),
    )
    for arguments, marker in cases:
        completed = run(sys.executable, "-m", "pystatsv1.cli", *arguments)
        assert completed.returncode == 0, completed.stdout + completed.stderr
        assert marker in completed.stdout


def test_psych_design_archive_rejects_traversal_member(tmp_path: Path) -> None:
    path = tmp_path / "unsafe.zip"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("../escape.txt", "bad")
        archive.writestr(
            MANIFEST_NAME,
            json.dumps(
                {
                    "schema_version": "pystatsv1-psych-design-bundle-manifest-v0.1",
                    "companion_version": "v0.1",
                    "package_version": "0.26.0",
                    "synthetic_data_only": True,
                    "real_data_authorized": False,
                    "files": [{"path": "../escape.txt", "sha256": "0" * 64}],
                }
            ),
        )
    with zipfile.ZipFile(path) as archive:
        manifest = _read_manifest_from_zip(archive)
        with pytest.raises(ValueError, match="unsafe"):
            _validate_zip_members(archive, manifest)


def test_psych_design_archive_rejects_symlink_member(tmp_path: Path) -> None:
    path = tmp_path / "symlink.zip"
    data = b"target"
    info = zipfile.ZipInfo("README.md")
    info.create_system = 3
    info.external_attr = (stat.S_IFLNK | 0o777) << 16
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(info, data)
        archive.writestr(
            MANIFEST_NAME,
            json.dumps(
                {
                    "schema_version": "pystatsv1-psych-design-bundle-manifest-v0.1",
                    "companion_version": "v0.1",
                    "package_version": "0.26.0",
                    "synthetic_data_only": True,
                    "real_data_authorized": False,
                    "files": [
                        {
                            "path": "README.md",
                            "sha256": hashlib.sha256(data).hexdigest(),
                        }
                    ],
                }
            ),
        )
    with zipfile.ZipFile(path) as archive:
        manifest = _read_manifest_from_zip(archive)
        with pytest.raises(RuntimeError, match="symlink"):
            _validate_zip_members(archive, manifest)


def test_unified_python_workflow_reproduces_all_ten_reference_results(
    tmp_path: Path,
) -> None:
    destination = tmp_path / "companion"
    initialize_psych_design(destination)
    completed = run(
        sys.executable,
        "scripts/python/run_all.py",
        cwd=destination,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "PYSTATSV1_PSYCH_DESIGN_ALL_PYTHON_OK studies=10" in completed.stdout
    for study in EXPECTED_STUDIES:
        slug = study.lower().replace("-", "_")
        result = destination / "outputs" / slug / "python_result.json"
        assert result.is_file(), study
        payload = json.loads(result.read_text(encoding="utf-8"))
        assert payload["study_id"] == study
        assert payload["synthetic_only"] is True


def test_swl_s02_mutation_cannot_preserve_governed_result(tmp_path: Path) -> None:
    destination = tmp_path / "companion"
    initialize_psych_design(destination)
    dataset = destination / "data/swl_s02_structured_study_routine.csv"
    rows = list(csv.DictReader(dataset.open(encoding="utf-8", newline="")))
    assert rows
    for row in rows:
        row["study_routine_group"] = (
            "standard_routine"
            if row["study_routine_group"] == "structured_routine"
            else "structured_routine"
        )
    with dataset.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    completed = run(
        sys.executable,
        "scripts/python/swl_s02_independent_groups.py",
        cwd=destination,
    )
    assert completed.returncode != 0
    assert "governed result drift" in (completed.stdout + completed.stderr)


def test_reviewer_packet_is_bounded_and_hash_manifested(tmp_path: Path) -> None:
    destination = tmp_path / "companion"
    initialize_psych_design(destination)
    study = "SWL-S02"
    slug = "swl_s02"
    completed = run(
        sys.executable,
        "scripts/python/swl_s02_independent_groups.py",
        cwd=destination,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    policy = json.loads(
        (destination / "VERIFICATION_POLICY.json").read_text(encoding="utf-8")
    )
    fields = next(row for row in policy["studies"] if row["study_id"] == study)[
        "parity_fields"
    ]
    python_result = json.loads(
        (destination / "outputs" / slug / "python_result.json").read_text(
            encoding="utf-8"
        )
    )["reported_fields"]
    r_result = destination / "outputs" / slug / "r_result.csv"
    with r_result.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["metric", "value"])
        for field in fields:
            writer.writerow([field, python_result[field]])
    for command in (
        [sys.executable, "scripts/verification/verify_swl_s02.py"],
        [sys.executable, "scripts/python/generate_figures.py", "--study", study],
        [sys.executable, "scripts/python/build_reviewer_packet.py", "--study", study],
    ):
        completed = run(*command, cwd=destination)
        assert completed.returncode == 0, completed.stdout + completed.stderr
    packet = destination / "outputs" / slug / "reviewer_packet"
    manifest = json.loads((packet / "MANIFEST.json").read_text(encoding="utf-8"))
    assert manifest["study_id"] == study
    assert manifest["synthetic_only"] is True
    names = {row["path"] for row in manifest["files"]}
    assert {
        "STUDY_INDEX_RECORD.json",
        "SOURCE_MANIFEST_RECORD.json",
        "DESIGN_CONTRACT.json",
        "MEASUREMENT_MAP.json",
        "DATA_LAYOUT_AUDIT.json",
        "PYTHON_RESULT.json",
        "R_RESULT.csv",
        "VERIFICATION_RECEIPT.json",
        "FIGURE_SPECS.json",
        "APA_SOURCE_MAP.json",
        "MATCHED_LIMITATION.md",
    }.issubset(names)
    for row in manifest["files"]:
        path = packet / row["path"]
        assert sha256(path) == row["sha256"]
    source_record = json.loads(
        (packet / "SOURCE_MANIFEST_RECORD.json").read_text(encoding="utf-8")
    )
    assert source_record["source_anchor"] == (
        "e88ff0f6f1aa1c4a946c72b97387f47b3c5311ae"
    )
    assert source_record["dataset_path"] == (
        "data/swl_s02_structured_study_routine.csv"
    )
    assert source_record["dataset_sha256"] == sha256(
        destination / source_record["dataset_path"]
    )
    figure_specs = json.loads(
        (packet / "FIGURE_SPECS.json").read_text(encoding="utf-8")
    )
    assert figure_specs["study_id"] == study
    assert len(figure_specs["specifications"]) == 1


def test_packaged_companion_excludes_outputs_and_caches() -> None:
    forbidden = {"outputs", "__pycache__", ".pytest_cache", ".venv", "venv"}
    with zipfile.ZipFile(ASSET) as archive:
        for name in archive.namelist():
            assert not (set(Path(name).parts) & forbidden), name
