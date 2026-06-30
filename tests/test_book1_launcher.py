from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path
from zipfile import ZipFile

import pytest

from pystatsv1.book1 import ASSET_NAME, MANIFEST_NAME, initialize_book1, packaged_book1_info, verify_book1_directory
from pystatsv1.cli import main


ROOT = Path(__file__).resolve().parents[1]
ASSET = ROOT / "src" / "pystatsv1" / "assets" / ASSET_NAME
BUILDER = ROOT / "tools" / "build_book1_companion_asset.py"


def _member_hashes(path: Path) -> dict[str, str]:
    with ZipFile(path) as zf:
        return {
            name: hashlib.sha256(zf.read(name)).hexdigest()
            for name in sorted(name for name in zf.namelist() if not name.endswith("/"))
        }


def test_book1_asset_has_expected_manifest_and_no_transient_members() -> None:
    assert ASSET.is_file()
    with ZipFile(ASSET) as zf:
        names = set(zf.namelist())
        manifest = json.loads(zf.read(MANIFEST_NAME).decode("utf-8"))
    assert manifest["schema_version"] == "pystatsv1-book1-bundle-manifest-v0.1"
    assert manifest["companion_version"] == "v0.1"
    assert manifest["synthetic_data_only"] is True
    assert "README.md" in names
    assert "scripts/python/generate_figures.py" in names
    assert "scripts/r/run_all.R" in names
    assert not any("__pycache__/" in name or name.endswith((".pyc", ".pyo")) for name in names)
    assert not any(name.startswith("outputs/") for name in names)
    modes = {row["path"]: row["mode"] for row in manifest["files"]}
    assert modes["README.md"] == "644"
    assert modes["scripts/python/ch12_apa_reporting.py"] == "755"
    assert modes["scripts/r/ch12_apa_reporting.R"] == "755"


def test_book1_manifest_uses_logical_modes_instead_of_host_permissions(tmp_path: Path) -> None:
    source = ROOT / "book1_companion" / "psych_stats_with_python_companion_v0_1"
    copied = tmp_path / "companion"
    shutil.copytree(source, copied)
    (copied / "README.md").chmod(0o755)
    (copied / "scripts" / "python" / "ch12_apa_reporting.py").chmod(0o644)
    rebuilt = tmp_path / ASSET_NAME
    subprocess.run(
        [sys.executable, str(BUILDER), "--source", str(copied), "--dest", str(rebuilt)],
        cwd=ROOT,
        check=True,
    )
    with ZipFile(rebuilt) as zf:
        manifest = json.loads(zf.read(MANIFEST_NAME).decode("utf-8"))
    modes = {row["path"]: row["mode"] for row in manifest["files"]}
    assert modes["README.md"] == "644"
    assert modes["scripts/python/ch12_apa_reporting.py"] == "755"


def test_book1_asset_is_current_against_source_snapshot(tmp_path: Path) -> None:
    rebuilt = tmp_path / ASSET_NAME
    subprocess.run(
        [sys.executable, str(BUILDER), "--dest", str(rebuilt)],
        cwd=ROOT,
        check=True,
    )
    assert _member_hashes(rebuilt) == _member_hashes(ASSET)


def test_book1_cli_init_and_verify(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    dest = tmp_path / "book1"
    assert main(["book1", "init", "--dest", str(dest)]) == 0
    assert (dest / "README.md").is_file()
    assert (dest / "data" / "ch10_correlation.csv").is_file()
    assert (dest / "scripts" / "python" / "generate_figures.py").is_file()
    assert main(["book1", "verify", "--dest", str(dest)]) == 0
    assert "PYSTATSV1_BOOK1_VERIFY_OK" in capsys.readouterr().out
    with pytest.raises(SystemExit, match="refusing to overwrite"):
        main(["book1", "init", "--dest", str(dest)])


def test_book1_verify_detects_source_tampering(tmp_path: Path) -> None:
    dest = tmp_path / "book1"
    initialize_book1(dest)
    readme = dest / "README.md"
    readme.write_text(readme.read_text(encoding="utf-8") + "\nchanged\n", encoding="utf-8")
    with pytest.raises(RuntimeError, match="hash mismatch"):
        verify_book1_directory(dest)


def test_book1_info_reads_packaged_manifest() -> None:
    manifest = packaged_book1_info()
    assert manifest["companion_version"] == "v0.1"
    assert len(manifest["files"]) >= 30


def test_book1_snapshot_targets_the_launcher_release_series() -> None:
    requirements = (
        ROOT / "book1_companion" / "psych_stats_with_python_companion_v0_1" / "requirements-book1-companion.txt"
    ).read_text(encoding="utf-8")
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert 'version = "0.24.1"' in pyproject
    assert "pystatsv1>=0.24.1,<0.25.0" in requirements
