from __future__ import annotations

import csv
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path
from zipfile import ZipFile

import pytest

from pystatsv1.book1 import (
    ASSET_NAME,
    DEFAULT_DEST_NAME,
    MAINTENANCE_NAME,
    MANIFEST_NAME,
    initialize_book1,
    packaged_book1_info,
    verify_book1_directory,
)
from pystatsv1.cli import main


ROOT = Path(__file__).resolve().parents[1]
HISTORICAL_SOURCE = (
    ROOT / "book1_companion" / "psych_stats_with_python_companion_v0_2"
)
CURRENT_SOURCE = (
    ROOT / "book1_companion" / "psych_stats_with_python_companion_v0_2_1"
)
HISTORICAL_ASSET_NAME = "psych_stats_with_python_companion_v0_2.zip"
HISTORICAL_ASSET = (
    ROOT / "src" / "pystatsv1" / "assets" / HISTORICAL_ASSET_NAME
)
CURRENT_ASSET = ROOT / "src" / "pystatsv1" / "assets" / ASSET_NAME
BUILDER = ROOT / "tools" / "build_book1_companion_asset.py"
HANDOFF_NAME = "BOOK1_PORTAL_HANDOFF_RECEIPT.json"
OLD_CSV_SHA256 = (
    "b8bebc818ce0349199029b1753e3d5dcb54411e879fc966061c8113377dc9125"
)
NEW_CSV_SHA256 = (
    "27dd7131bb304aad6d7d69d26462df021c6f1dc2e9889fa4d69e508ae4d605d6"
)
HISTORICAL_ASSET_SHA256 = (
    "daac70c08bdec18c2b2f702d8fa57f76ab2635dd5a522c2a0620d66accbdf2de"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _member_hashes(path: Path) -> dict[str, str]:
    with ZipFile(path) as zf:
        return {
            name: hashlib.sha256(zf.read(name)).hexdigest()
            for name in sorted(
                name for name in zf.namelist() if not name.endswith("/")
            )
        }


def _manifest(path: Path) -> dict:
    with ZipFile(path) as zf:
        return json.loads(zf.read(MANIFEST_NAME).decode("utf-8"))


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_book1_current_asset_has_expected_v021_manifest_and_no_transient_members() -> None:
    assert CURRENT_ASSET.is_file()
    with ZipFile(CURRENT_ASSET) as zf:
        names = set(zf.namelist())
        manifest = json.loads(zf.read(MANIFEST_NAME).decode("utf-8"))
    assert manifest["schema_version"] == "pystatsv1-book1-bundle-manifest-v0.1"
    assert manifest["companion_version"] == "v0.2.1"
    assert manifest["synthetic_data_only"] is True
    assert "README.md" in names
    assert HANDOFF_NAME in names
    assert MAINTENANCE_NAME in names
    assert "BOOK1_DESIGN_CONTRACT.json" in names
    assert "scripts/python/book1_design_contract.py" in names
    assert "scripts/python/audit_design_contract.py" in names
    assert "tests/test_book1_design_contract.py" in names
    assert "scripts/python/generate_figures.py" in names
    assert "scripts/r/run_all.R" in names
    assert not any(
        "__pycache__/" in name or name.endswith((".pyc", ".pyo"))
        for name in names
    )
    assert not any(name.startswith("outputs/") for name in names)
    modes = {row["path"]: row["mode"] for row in manifest["files"]}
    assert modes["README.md"] == "644"
    assert modes["scripts/python/ch12_apa_reporting.py"] == "755"
    assert modes["scripts/r/ch12_apa_reporting.R"] == "755"


def test_book1_current_asset_uses_canonical_posix_order_and_logical_modes(
    tmp_path: Path,
) -> None:
    with ZipFile(CURRENT_ASSET) as zf:
        manifest = json.loads(zf.read(MANIFEST_NAME).decode("utf-8"))
    paths = [row["path"] for row in manifest["files"]]
    assert paths == sorted(paths)

    copied = tmp_path / "companion"
    shutil.copytree(CURRENT_SOURCE, copied)
    (copied / "README.md").chmod(0o755)
    (copied / "scripts" / "python" / "ch12_apa_reporting.py").chmod(0o644)
    rebuilt = tmp_path / ASSET_NAME
    subprocess.run(
        [
            sys.executable,
            str(BUILDER),
            "--source",
            str(copied),
            "--dest",
            str(rebuilt),
        ],
        cwd=ROOT,
        check=True,
    )
    modes = {row["path"]: row["mode"] for row in _manifest(rebuilt)["files"]}
    assert modes["README.md"] == "644"
    assert modes["scripts/python/ch12_apa_reporting.py"] == "755"


def test_book1_current_asset_is_deterministic_and_current_against_v021_source(
    tmp_path: Path,
) -> None:
    rebuilt_a = tmp_path / "a.zip"
    rebuilt_b = tmp_path / "b.zip"
    for destination in (rebuilt_a, rebuilt_b):
        subprocess.run(
            [sys.executable, str(BUILDER), "--dest", str(destination)],
            cwd=ROOT,
            check=True,
        )
    assert rebuilt_a.read_bytes() == rebuilt_b.read_bytes()
    assert _member_hashes(rebuilt_a) == _member_hashes(CURRENT_ASSET)


def test_book1_historical_v02_asset_remains_rebuildable_and_unchanged(
    tmp_path: Path,
) -> None:
    assert _sha256(HISTORICAL_ASSET) == HISTORICAL_ASSET_SHA256
    rebuilt = tmp_path / HISTORICAL_ASSET_NAME
    subprocess.run(
        [
            sys.executable,
            str(BUILDER),
            "--source",
            str(HISTORICAL_SOURCE),
            "--dest",
            str(rebuilt),
        ],
        cwd=ROOT,
        check=True,
    )
    assert _member_hashes(rebuilt) == _member_hashes(HISTORICAL_ASSET)
    assert _manifest(rebuilt)["companion_version"] == "v0.2"
    assert MAINTENANCE_NAME not in _member_hashes(rebuilt)


def test_book1_v02_portal_handoff_preserves_data_and_scripts() -> None:
    receipt = json.loads(
        (HISTORICAL_SOURCE / HANDOFF_NAME).read_text(encoding="utf-8")
    )
    assert receipt["companion_version"] == "v0.2"
    assert receipt["portal_tag"] == "book1-companion-v0.2-candidate"
    assert receipt["portal_commit"] == "20076607ebf37245f0eb9ed7c5a56f56a042a8f5"
    assert receipt["synthetic_data_only"] is True
    hashes = receipt["unchanged_payload_sha256"]
    assert hashes
    for rel, expected in hashes.items():
        path = HISTORICAL_SOURCE / rel
        assert path.is_file(), rel
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected, rel
    adjustments = {
        row["path"]: row
        for row in receipt["lint_only_release_adjustments"]
    }
    assert set(adjustments) == {
        "scripts/python/ch12_apa_reporting.py",
        "scripts/python/finalize_apa_reporting_audit.py",
    }
    for rel, row in adjustments.items():
        path = HISTORICAL_SOURCE / rel
        assert hashlib.sha256(path.read_bytes()).hexdigest() == row["release_source_sha256"]
        assert row["portal_candidate_sha256"] != row["release_source_sha256"]

    workflow_repairs = {
        row["path"]: row
        for row in receipt["pretag_public_figure_workflow_repair_adjustments"]
    }
    assert set(workflow_repairs) == {"scripts/python/generate_figures.py"}
    repair = workflow_repairs["scripts/python/generate_figures.py"]
    assert (
        hashlib.sha256(
            (HISTORICAL_SOURCE / repair["path"]).read_bytes()
        ).hexdigest()
        == repair["release_source_sha256"]
    )
    assert repair["portal_candidate_sha256"] != repair["release_source_sha256"]
    assert "public_release guard" in repair["reason"]


def test_book1_v021_maintenance_receipt_and_ch08_id_only_contract() -> None:
    old_csv = HISTORICAL_SOURCE / "data" / "ch08_two_way_anova.csv"
    new_csv = CURRENT_SOURCE / "data" / "ch08_two_way_anova.csv"
    old_rows = _read_csv(old_csv)
    new_rows = _read_csv(new_csv)

    assert _sha256(old_csv) == OLD_CSV_SHA256
    assert _sha256(new_csv) == NEW_CSV_SHA256
    assert len(old_rows) == len(new_rows) == 48

    ids = [row["participant_id"] for row in new_rows]
    assert ids == [f"ch08_{number:03d}" for number in range(1, 49)]
    assert len(set(ids)) == 48

    analytical_columns = ("strategy", "feedback", "test_score")
    assert [
        tuple(row[column] for column in analytical_columns)
        for row in old_rows
    ] == [
        tuple(row[column] for column in analytical_columns)
        for row in new_rows
    ]

    receipt = json.loads(
        (CURRENT_SOURCE / MAINTENANCE_NAME).read_text(encoding="utf-8")
    )
    assert receipt["schema_version"] == "book1-companion-maintenance-receipt-v0.1"
    assert receipt["companion_version"] == "v0.2.1"
    assert receipt["synthetic_data_only"] is True
    assert receipt["correction"]["old_sha256"] == OLD_CSV_SHA256
    assert receipt["correction"]["new_sha256"] == NEW_CSV_SHA256
    assert receipt["change_contract"]["participant_id_changed"] is True
    assert receipt["change_contract"]["statistical_analysis_scripts_unchanged"] is True
    assert receipt["data_contract_after_correction"]["unique_participant_id_count"] == 48
    assert receipt["data_contract_after_correction"]["duplicate_participant_row_count"] == 0
    assert receipt["statistical_verification"]["chapter8_parity_status"] == "PASS"
    assert receipt["figure_verification"]["byte_identical"] is True
    assert receipt["lineage"]["historical_portal_handoff_receipt_preserved_unchanged"] is True

    assert (
        (HISTORICAL_SOURCE / HANDOFF_NAME).read_bytes()
        == (CURRENT_SOURCE / HANDOFF_NAME).read_bytes()
    )

    manifest = _manifest(CURRENT_ASSET)
    hashes = {row["path"]: row["sha256"] for row in manifest["files"]}
    assert hashes["data/ch08_two_way_anova.csv"] == NEW_CSV_SHA256
    assert MAINTENANCE_NAME in hashes


def test_book1_v021_figure_contract_has_six_source_faithful_grayscale_figures() -> None:
    spec = json.loads(
        (CURRENT_SOURCE / "figures_specs.json").read_text(encoding="utf-8")
    )
    assert spec["companion_version"] == "v0.2.1"
    assert spec["required_pystatsv1_release"] == "0.25.2"
    assert spec["release_status"] == "public_release"
    assert spec["print_profile"] == "high-contrast-grayscale"
    assert spec["minimum_effective_ppi"] >= 300
    figures = {row["figure_id"]: row for row in spec["figures"]}
    assert set(figures) == {
        "fig_03_1_distribution_zscore",
        "fig_06_1_paired_change",
        "fig_08_1_interaction",
        "fig_09_1_repeated_trajectory",
        "fig_10_1_correlation_scatter",
        "fig_11_1_regression_scatter",
    }


def test_book1_v021_public_figure_workflow_runs_from_packaged_asset(
    tmp_path: Path,
) -> None:
    dest = tmp_path / "book1"
    initialize_book1(dest)

    completed = subprocess.run(
        [sys.executable, "scripts/python/generate_figures.py"],
        cwd=dest,
        check=True,
        text=True,
        capture_output=True,
    )
    assert "PYSTATSV1_BOOK1_V021_PUBLIC_FIGURES_OK" in completed.stdout

    manifest = json.loads(
        (dest / "outputs" / "figure_manifest.json").read_text(encoding="utf-8")
    )
    assert manifest["companion_version"] == "v0.2.1"
    assert manifest["release_status"] == "public_release"
    assert manifest["print_profile"] == "high-contrast-grayscale"
    assert len(manifest["figures"]) == 6
    for row in manifest["figures"]:
        assert (dest / "outputs" / row["output_filename"]).is_file()


@pytest.mark.parametrize(
    "release_status",
    [None, "candidate_not_public", "unknown_status"],
)
def test_book1_v021_public_figure_workflow_rejects_nonpublic_status(
    tmp_path: Path,
    release_status: str | None,
) -> None:
    dest = tmp_path / "book1"
    initialize_book1(dest)
    spec_path = dest / "figures_specs.json"
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    if release_status is None:
        spec.pop("release_status", None)
    else:
        spec["release_status"] = release_status
    spec_path.write_text(json.dumps(spec, indent=2) + "\n", encoding="utf-8")

    completed = subprocess.run(
        [sys.executable, "scripts/python/generate_figures.py"],
        cwd=dest,
        check=False,
        text=True,
        capture_output=True,
    )
    assert completed.returncode != 0
    assert "public release status must remain explicit" in completed.stderr
    assert not (dest / "outputs").exists()


def test_book1_cli_init_and_verify_v021(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    dest = tmp_path / "book1"
    assert main(["book1", "init", "--dest", str(dest)]) == 0
    assert (dest / "README.md").is_file()
    assert (dest / "data" / "ch10_correlation.csv").is_file()
    assert (dest / "scripts" / "python" / "generate_figures.py").is_file()
    assert (dest / HANDOFF_NAME).is_file()
    assert (dest / MAINTENANCE_NAME).is_file()
    assert main(["book1", "verify", "--dest", str(dest)]) == 0
    assert (
        "PYSTATSV1_BOOK1_VERIFY_OK companion_version=v0.2.1"
        in capsys.readouterr().out
    )
    with pytest.raises(SystemExit, match="refusing to overwrite"):
        main(["book1", "init", "--dest", str(dest)])


def test_book1_default_destination_is_v021() -> None:
    assert DEFAULT_DEST_NAME == "psych_stats_with_python_companion_v0_2_1"


def test_book1_verify_detects_source_tampering(tmp_path: Path) -> None:
    dest = tmp_path / "book1"
    initialize_book1(dest)
    readme = dest / "README.md"
    readme.write_text(
        readme.read_text(encoding="utf-8") + "\nchanged\n",
        encoding="utf-8",
    )
    with pytest.raises(RuntimeError, match="hash mismatch"):
        verify_book1_directory(dest)


def test_book1_info_reads_packaged_v021_manifest() -> None:
    manifest = packaged_book1_info()
    assert manifest["companion_version"] == "v0.2.1"
    assert len(manifest["files"]) >= 38


def test_book1_builder_requires_maintenance_receipt_for_v021(
    tmp_path: Path,
) -> None:
    copied = tmp_path / "companion"
    shutil.copytree(CURRENT_SOURCE, copied)
    (copied / MAINTENANCE_NAME).unlink()
    completed = subprocess.run(
        [
            sys.executable,
            str(BUILDER),
            "--source",
            str(copied),
            "--dest",
            str(tmp_path / "invalid.zip"),
        ],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )
    assert completed.returncode != 0
    assert MAINTENANCE_NAME in (completed.stdout + completed.stderr)


def test_book1_historical_and_current_release_bindings_are_explicit() -> None:
    old_requirements = (
        HISTORICAL_SOURCE / "requirements-book1-companion.txt"
    ).read_text(encoding="utf-8")
    new_requirements = (
        CURRENT_SOURCE / "requirements-book1-companion.txt"
    ).read_text(encoding="utf-8")
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert "pystatsv1>=0.25.0,<0.26.0" in old_requirements
    assert "pystatsv1>=0.25.2,<0.26.0" in new_requirements
    assert 'version = "0.25.2"' in pyproject

def test_book1_v021_design_audit_source_route_passes_without_writing(
    tmp_path: Path,
) -> None:
    copied = tmp_path / "companion"
    shutil.copytree(CURRENT_SOURCE, copied, ignore=shutil.ignore_patterns("outputs"))
    completed = subprocess.run(
        [
            sys.executable,
            str(copied / "scripts" / "python" / "audit_design_contract.py"),
            "--root",
            str(copied),
            "--check-only",
        ],
        cwd=copied,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "BOOK1_COMPANION_DESIGN_AUDIT_OK" in completed.stdout
    assert not (copied / "outputs" / "design").exists()


def test_book1_v021_packaged_design_audit_writes_deterministic_receipts(
    tmp_path: Path,
) -> None:
    dest = tmp_path / "book1"
    initialize_book1(dest)
    command = [
        sys.executable,
        str(dest / "scripts" / "python" / "audit_design_contract.py"),
        "--root",
        str(dest),
    ]
    first = subprocess.run(
        command,
        cwd=dest,
        text=True,
        capture_output=True,
        check=False,
    )
    assert first.returncode == 0, first.stdout + first.stderr
    assert "BOOK1_COMPANION_DESIGN_AUDIT_OK" in first.stdout
    receipt = dest / "outputs" / "design" / "BOOK1_DESIGN_AUDIT_RECEIPT.json"
    summary = dest / "outputs" / "design" / "BOOK1_DESIGN_AUDIT_SUMMARY.md"
    first_receipt = receipt.read_bytes()
    first_summary = summary.read_bytes()
    second = subprocess.run(
        command,
        cwd=dest,
        text=True,
        capture_output=True,
        check=False,
    )
    assert second.returncode == 0, second.stdout + second.stderr
    assert first_receipt == receipt.read_bytes()
    assert first_summary == summary.read_bytes()
    payload = json.loads(receipt.read_text(encoding="utf-8"))
    assert payload["overall_status"] == "PASS"
    assert payload["semantic_design_status"] == "PASS"
    assert payload["release_fingerprint_status"] == "PASS"
