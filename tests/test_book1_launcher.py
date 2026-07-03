from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path
from zipfile import ZipFile

import pytest

from pystatsv1.book1 import ASSET_NAME, DEFAULT_DEST_NAME, MANIFEST_NAME, initialize_book1, packaged_book1_info, verify_book1_directory
from pystatsv1.cli import main


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "book1_companion" / "psych_stats_with_python_companion_v0_2"
ASSET = ROOT / "src" / "pystatsv1" / "assets" / ASSET_NAME
BUILDER = ROOT / "tools" / "build_book1_companion_asset.py"
HANDOFF_NAME = "BOOK1_PORTAL_HANDOFF_RECEIPT.json"


def _member_hashes(path: Path) -> dict[str, str]:
    with ZipFile(path) as zf:
        return {
            name: hashlib.sha256(zf.read(name)).hexdigest()
            for name in sorted(name for name in zf.namelist() if not name.endswith("/"))
        }


def _manifest(path: Path) -> dict:
    with ZipFile(path) as zf:
        return json.loads(zf.read(MANIFEST_NAME).decode("utf-8"))


def test_book1_asset_has_expected_v02_manifest_and_no_transient_members() -> None:
    assert ASSET.is_file()
    with ZipFile(ASSET) as zf:
        names = set(zf.namelist())
        manifest = json.loads(zf.read(MANIFEST_NAME).decode("utf-8"))
    assert manifest["schema_version"] == "pystatsv1-book1-bundle-manifest-v0.1"
    assert manifest["companion_version"] == "v0.2"
    assert manifest["synthetic_data_only"] is True
    assert "README.md" in names
    assert HANDOFF_NAME in names
    assert "scripts/python/generate_figures.py" in names
    assert "scripts/r/run_all.R" in names
    assert not any("__pycache__/" in name or name.endswith((".pyc", ".pyo")) for name in names)
    assert not any(name.startswith("outputs/") for name in names)
    modes = {row["path"]: row["mode"] for row in manifest["files"]}
    assert modes["README.md"] == "644"
    assert modes["scripts/python/ch12_apa_reporting.py"] == "755"
    assert modes["scripts/r/ch12_apa_reporting.R"] == "755"


def test_book1_v02_uses_canonical_posix_order_and_logical_modes(tmp_path: Path) -> None:
    with ZipFile(ASSET) as zf:
        manifest = json.loads(zf.read(MANIFEST_NAME).decode("utf-8"))
    paths = [row["path"] for row in manifest["files"]]
    assert paths == sorted(paths)

    copied = tmp_path / "companion"
    shutil.copytree(SOURCE, copied)
    (copied / "README.md").chmod(0o755)
    (copied / "scripts" / "python" / "ch12_apa_reporting.py").chmod(0o644)
    rebuilt = tmp_path / ASSET_NAME
    subprocess.run(
        [sys.executable, str(BUILDER), "--source", str(copied), "--dest", str(rebuilt)],
        cwd=ROOT,
        check=True,
    )
    modes = {row["path"]: row["mode"] for row in _manifest(rebuilt)["files"]}
    assert modes["README.md"] == "644"
    assert modes["scripts/python/ch12_apa_reporting.py"] == "755"


def test_book1_asset_is_current_against_v02_source_snapshot(tmp_path: Path) -> None:
    rebuilt = tmp_path / ASSET_NAME
    subprocess.run(
        [sys.executable, str(BUILDER), "--dest", str(rebuilt)],
        cwd=ROOT,
        check=True,
    )
    assert _member_hashes(rebuilt) == _member_hashes(ASSET)


def test_book1_v02_portal_handoff_preserves_data_and_scripts() -> None:
    receipt = json.loads((SOURCE / HANDOFF_NAME).read_text(encoding="utf-8"))
    assert receipt["companion_version"] == "v0.2"
    assert receipt["portal_tag"] == "book1-companion-v0.2-candidate"
    assert receipt["portal_commit"] == "20076607ebf37245f0eb9ed7c5a56f56a042a8f5"
    assert receipt["synthetic_data_only"] is True
    hashes = receipt["unchanged_payload_sha256"]
    assert hashes
    for rel, expected in hashes.items():
        path = SOURCE / rel
        assert path.is_file(), rel
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected, rel
    adjustments = {row["path"]: row for row in receipt["lint_only_release_adjustments"]}
    assert set(adjustments) == {
        "scripts/python/ch12_apa_reporting.py",
        "scripts/python/finalize_apa_reporting_audit.py",
    }
    for rel, row in adjustments.items():
        path = SOURCE / rel
        assert hashlib.sha256(path.read_bytes()).hexdigest() == row["release_source_sha256"]
        assert row["portal_candidate_sha256"] != row["release_source_sha256"]
    ch12 = (SOURCE / "scripts/python/ch12_apa_reporting.py").read_text(encoding="utf-8")
    audit = (SOURCE / "scripts/python/finalize_apa_reporting_audit.py").read_text(encoding="utf-8")
    assert "from pathlib import Path" not in ch12
    assert " ROOT," not in ch12
    assert " rounded," not in ch12
    assert "from pathlib import Path" not in audit


def test_book1_v02_figure_contract_has_six_source_faithful_grayscale_figures() -> None:
    spec = json.loads((SOURCE / "figures_specs.json").read_text(encoding="utf-8"))
    assert spec["companion_version"] == "v0.2"
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
    assert figures["fig_10_1_correlation_scatter"]["source_csv"] == "data/ch10_correlation.csv"
    assert figures["fig_11_1_regression_scatter"]["source_csv"] == "data/ch11_regression.csv"
    assert figures["fig_10_1_correlation_scatter"]["analysis_contract"]["apa_source_id"] == "ch10"
    assert figures["fig_11_1_regression_scatter"]["analysis_contract"]["apa_source_id"] == "ch11"


def test_book1_cli_init_and_verify_v02(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    dest = tmp_path / "book1"
    assert main(["book1", "init", "--dest", str(dest)]) == 0
    assert (dest / "README.md").is_file()
    assert (dest / "data" / "ch10_correlation.csv").is_file()
    assert (dest / "scripts" / "python" / "generate_figures.py").is_file()
    assert (dest / HANDOFF_NAME).is_file()
    assert main(["book1", "verify", "--dest", str(dest)]) == 0
    assert "PYSTATSV1_BOOK1_VERIFY_OK companion_version=v0.2" in capsys.readouterr().out
    with pytest.raises(SystemExit, match="refusing to overwrite"):
        main(["book1", "init", "--dest", str(dest)])


def test_book1_default_destination_is_v02() -> None:
    assert DEFAULT_DEST_NAME == "psych_stats_with_python_companion_v0_2"


def test_book1_verify_detects_source_tampering(tmp_path: Path) -> None:
    dest = tmp_path / "book1"
    initialize_book1(dest)
    readme = dest / "README.md"
    readme.write_text(readme.read_text(encoding="utf-8") + "\nchanged\n", encoding="utf-8")
    with pytest.raises(RuntimeError, match="hash mismatch"):
        verify_book1_directory(dest)


def test_book1_info_reads_packaged_v02_manifest() -> None:
    manifest = packaged_book1_info()
    assert manifest["companion_version"] == "v0.2"
    assert len(manifest["files"]) >= 37


def test_book1_snapshot_targets_the_launcher_release_series() -> None:
    requirements = (SOURCE / "requirements-book1-companion.txt").read_text(encoding="utf-8")
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert 'version = "0.25.0"' in pyproject
    assert "pystatsv1>=0.25.0,<0.26.0" in requirements
