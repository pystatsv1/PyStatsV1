from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROOF = ROOT / "release_proofs" / "psych_design_v0_1"
EVIDENCE = PROOF / "evidence"
ASSET = (
    ROOT
    / "src"
    / "pystatsv1"
    / "assets"
    / "psychological_statistics_by_design_companion_v0_1.zip"
)
SOURCE = (
    ROOT
    / "psych_design_companion"
    / "psychological_statistics_by_design_companion_v0_1"
)
CHECKER = ROOT / "tools" / "check_psych_design_release_proof.py"
COMPARATOR = ROOT / "tools" / "compare_psych_design_release_proofs.py"
EXPECTED_STUDIES = [f"SWL-S{number:02d}" for number in range(1, 11)]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def run(*command: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(command),
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def test_release_proof_contract_freezes_candidate_and_closed_gates() -> None:
    contract = load(PROOF / "RELEASE_PROOF_CONTRACT.json")
    identity = contract["release_identity"]
    assert contract["dropin"] == "034"
    assert contract["baseline"]["candidate_commit"] == (
        "58d92f85b865cb657bf49c731fefc381970c8bda"
    )
    assert contract["baseline"]["candidate_tag"] == (
        "psych-design-companion-v0-1-candidate"
    )
    assert contract["baseline"]["reserved_final_release_tag"] == "v0.26.0"
    assert identity["package_version"] == "0.26.0"
    assert identity["companion_version"] == "v0.1"
    assert identity["wheel_sha256"] == (
        "62a5c26577867f22c7bbf15dcf4253da749fe703fcec42ffc19b72454af8fa05"
    )
    assert identity["asset_sha256"] == sha256(ASSET)
    assert identity["immutable_source_file_count"] == 151
    assert identity["study_ids"] == EXPECTED_STUDIES
    assert contract["cross_platform_comparison"]["renderer_tolerance"][
        "png_byte_identity_required"
    ] is False
    lifecycle = contract["lifecycle"]
    assert lifecycle["candidate_implementation_passed"] is True
    assert lifecycle["clean_wsl_proof"] == "required_before_pull_request_and_merge"
    assert lifecycle["public_pypi_release_authorized"] is False
    assert lifecycle["portal_release_authorized"] is False
    assert lifecycle["book_binding_authorized"] is False
    assert lifecycle["real_data_authorized"] is False


def test_candidate_asset_and_source_tree_remain_byte_frozen() -> None:
    contract = load(PROOF / "RELEASE_PROOF_CONTRACT.json")
    identity = contract["release_identity"]
    with zipfile.ZipFile(ASSET) as archive:
        manifest_bytes = archive.read("COMPANION_MANIFEST.json")
        index_bytes = archive.read("STUDY_INDEX.json")
        manifest = json.loads(manifest_bytes)
        assert hashlib.sha256(manifest_bytes).hexdigest() == identity[
            "asset_manifest_sha256"
        ]
        assert hashlib.sha256(index_bytes).hexdigest() == identity[
            "study_index_sha256"
        ]
        assert len(manifest["files"]) == 151
        for row in manifest["files"]:
            path = SOURCE / row["path"]
            assert path.is_file(), row["path"]
            assert sha256(path) == row["sha256"]
            assert hashlib.sha256(archive.read(row["path"])).hexdigest() == row[
                "sha256"
            ]
    assert not (SOURCE / "outputs").exists()


def test_release_proof_source_checker_passes() -> None:
    completed = run(sys.executable, str(CHECKER), "--phase", "source")
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "PYSTATSV1_PSYCH_DESIGN_RELEASE_PROOF_VERIFY_OK" in completed.stdout


def test_windows_ci_fetches_candidate_tag_for_release_proof_checker() -> None:
    workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(
        encoding="utf-8"
    )
    windows_job = workflow.split("  windows-py310:", maxsplit=1)[1]
    checkout = windows_job.split("      - name: Set up Python", maxsplit=1)[0]
    assert "uses: actions/checkout@v4" in checkout
    assert "fetch-depth: 0" in checkout


def _receipt(role: str, png_suffix: str = "a") -> dict:
    studies = {}
    source_bindings = {}
    for study in EXPECTED_STUDIES:
        studies[study] = {
            "verification_category": "V3_V4" if study == "SWL-S08" else "V2",
            "python_result_sha256": "1" * 64,
            "python_reported_fields": {"estimate": "1.25"},
            "r_result_sha256": "2" * 64,
            "r_metrics": {"estimate": "1.25"},
            "verification_receipt_sha256": "3" * 64,
            "verification_status": "pass",
            "verification_comparisons": [
                {
                    "field": "estimate",
                    "python": "1.25",
                    "r": "1.25",
                    "absolute_difference": "0",
                    "allowed_absolute_difference": "1e-08",
                    "status": "pass",
                }
            ],
            "v4_documented_not_equal_fields": ["software_df"]
            if study == "SWL-S08"
            else [],
            "reviewer_packet_membership": [f"file-{number}" for number in range(12)],
            "reviewer_packet_file_count": 12,
            "reviewer_packet_source_hashes": {"DESIGN_CONTRACT.json": "4" * 64},
            "apa_runtime_binding_sha256": "5" * 64,
            "matched_limitation_runtime_sha256": "6" * 64,
            "figures": {
                "manifest_semantics": {
                    "study_id": study,
                    "figures": [
                        {
                            "output": f"{study}.png",
                            "role": "primary",
                            "dpi": 300,
                            "grayscale": True,
                            "pixel_dimensions": [1800, 1200],
                        }
                    ],
                },
                "png_hashes": {f"{study}.png": png_suffix * 64},
            },
        }
        source_bindings[study] = {
            "dataset": {f"data/{study}.csv": "7" * 64},
            "design": {f"design/{study}.json": "8" * 64},
            "measurement": {f"measurement/{study}.json": "9" * 64},
            "apa_source_maps": {f"apa/{study}.json": "a" * 64},
            "matched_limitations": {f"limits/{study}.json": "b" * 64},
            "figure_specs": {f"figures/{study}.json": "c" * 64},
        }
    return {
        "schema_version": "pystatsv1-psych-design-clean-reader-proof-v0.1",
        "status": "pass",
        "platform_role": role,
        "candidate_commit": "58d92f85b865cb657bf49c731fefc381970c8bda",
        "candidate_tag": "psych-design-companion-v0-1-candidate",
        "package_version": "0.26.0",
        "companion_version": "v0.1",
        "synthetic_only": True,
        "real_data_authorized": False,
        "artifact_identity": {
            "wheel_name": "pystatsv1-0.26.0-py3-none-any.whl",
            "wheel_sha256": "d" * 64,
            "wheel_bytes": 123,
            "asset_sha256": "e" * 64,
            "asset_bytes": 456,
            "source_manifest_sha256": "f" * 64,
            "study_index_sha256": "0" * 64,
            "source_file_count": 151,
            "source_manifest_status": "pass",
        },
        "command_markers": {"marker": True},
        "source_bindings": source_bindings,
        "study_evidence": studies,
        "publication_gates": {
            "pypi_release_authorized": False,
            "portal_release_authorized": False,
            "book_binding_authorized": False,
            "real_data_authorized": False,
        },
    }


def test_cross_platform_comparison_allows_only_png_byte_differences(
    tmp_path: Path,
) -> None:
    ubuntu = tmp_path / "ubuntu.json"
    wsl = tmp_path / "wsl.json"
    comparison = tmp_path / "comparison.json"
    readiness = tmp_path / "readiness.json"
    ubuntu.write_text(json.dumps(_receipt("ubuntu", "a")), encoding="utf-8")
    wsl.write_text(json.dumps(_receipt("wsl", "b")), encoding="utf-8")
    completed = run(
        sys.executable,
        str(COMPARATOR),
        "--ubuntu",
        str(ubuntu),
        "--wsl",
        str(wsl),
        "--comparison",
        str(comparison),
        "--readiness",
        str(readiness),
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    result = load(comparison)
    state = load(readiness)
    assert result["status"] == "pass"
    assert all(
        row["status"] == "allowed_renderer_difference"
        for row in result["png_renderer_comparison"]["studies"].values()
    )
    assert state["technical_release_ready"] is True
    assert state["pypi_release_authorized"] is False
    assert state["portal_release_authorized"] is False
    assert state["book_binding_authorized"] is False


def test_cross_platform_comparison_rejects_v2_numerical_drift(
    tmp_path: Path,
) -> None:
    left = _receipt("ubuntu")
    right = _receipt("wsl")
    right["study_evidence"]["SWL-S02"]["python_reported_fields"]["estimate"] = "1.26"
    ubuntu = tmp_path / "ubuntu.json"
    wsl = tmp_path / "wsl.json"
    comparison = tmp_path / "comparison.json"
    readiness = tmp_path / "readiness.json"
    ubuntu.write_text(json.dumps(left), encoding="utf-8")
    wsl.write_text(json.dumps(right), encoding="utf-8")
    completed = run(
        sys.executable,
        str(COMPARATOR),
        "--ubuntu",
        str(ubuntu),
        "--wsl",
        str(wsl),
        "--comparison",
        str(comparison),
        "--readiness",
        str(readiness),
    )
    assert completed.returncode != 0
    assert "SWL-S02.python_reported_fields" in completed.stderr
    assert load(readiness)["technical_release_ready"] is False


def test_wsl_runner_requires_linux_home_and_checksum_verification() -> None:
    text = (PROOF / "run_wsl_release_proof.sh").read_text(encoding="utf-8")
    assert "sha256sum -c PYSTATSV1_DROPIN_034_WSL_KIT_SHA256SUMS.txt" in text
    assert 'case "$KIT_DIR" in' in text
    assert "/mnt/*)" in text
    assert "PYSTATSV1_DROPIN_034_WSL_PROOF_COMPLETE" in text
    assert "wsl2|microsoft-standard" in text
    assert "cmd.exe" in text
    assert "wsl.exe" in text


def test_release_receipts_do_not_persist_absolute_reader_paths() -> None:
    text = (ROOT / "tools" / "run_psych_design_clean_reader_proof.py").read_text(
        encoding="utf-8"
    )
    assert '"workspace": str(resolved)' not in text
    assert '"python_executable": str(venv_python)' not in text
    assert '"absolute_workspace_path_recorded": False' in text
    checker = CHECKER.read_text(encoding="utf-8")
    assert 'workspace.get("is_wsl2") is not True' in checker


def test_publication_workflow_is_manual_and_annotated_tag_gated() -> None:
    text = (ROOT / ".github/workflows/pypi-publish.yml").read_text(encoding="utf-8")
    assert "workflow_dispatch:" in text
    assert "git cat-file -t" in text
    assert 'if [ "$object_type" != "tag" ]' in text
    assert "python tools/check_release_tag.py" in text
    assert "psych-design-companion-v0-1-candidate" not in text


def test_readiness_state_is_coherent_and_never_opens_release_gates() -> None:
    state = load(EVIDENCE / "PSYCH_DESIGN_RELEASE_READINESS.json")
    assert state["candidate_implementation_passed"] is True
    ubuntu = state["clean_ubuntu_proof_passed"]
    wsl = state["clean_wsl_proof_passed"]
    comparison = state["cross_platform_comparison_passed"]
    ready = state["technical_release_ready"]
    assert (ubuntu, wsl, comparison, ready) in {
        (False, False, False, False),
        (True, False, False, False),
        (True, True, True, True),
    }
    assert state["pypi_release_authorized"] is False
    assert state["portal_release_authorized"] is False
    assert state["book_binding_authorized"] is False
    assert state["real_data_authorized"] is False
