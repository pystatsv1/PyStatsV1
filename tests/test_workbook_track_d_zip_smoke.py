# SPDX-License-Identifier: MIT

from __future__ import annotations

from pathlib import Path

import zipfile


def test_workbook_track_d_zip_exists_and_has_expected_files() -> None:
    """Ensure the Track D workbook template zip is present and looks sane."""
    zip_path = Path("src/pystatsv1/assets/workbook_track_d.zip")
    assert zip_path.exists(), "workbook_track_d.zip missing"

    with zipfile.ZipFile(zip_path) as zf:
        names = set(zf.namelist())

    expected = {
        "README.md",
        "Makefile",
        "requirements.txt",
        "scripts/_cli.py",
        "scripts/d00_peek_data.py",
        "scripts/d00_setup_data.py",
        "scripts/sim_business_ledgerlab.py",
        "scripts/sim_business_nso_v1.py",
        "scripts/business_validate_dataset.py",
        "tests/test_business_smoke.py",
        "data/synthetic/ledgerlab_ch01/.gitkeep",
        "data/synthetic/nso_v1/.gitkeep",
    }

    # Convenience wrappers: d01.py .. d23.py
    expected |= {f"scripts/d{i:02d}.py" for i in range(1, 24)}

    missing = expected - names
    assert not missing, f"Missing from workbook zip: {sorted(missing)}"


def test_extract_workbook_template_has_expected_layout(tmp_path: Path) -> None:
    zip_path = Path("src/pystatsv1/assets/workbook_track_d.zip")

    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(tmp_path)

    assert (tmp_path / "README.md").exists()
    assert (tmp_path / "scripts" / "d00_peek_data.py").exists()
    assert (tmp_path / "scripts" / "d00_setup_data.py").exists()

    # Spot-check a few wrapper scripts.
    assert (tmp_path / "scripts" / "d01.py").exists()
    assert (tmp_path / "scripts" / "d14.py").exists()
    assert (tmp_path / "scripts" / "d23.py").exists()


def test_workbook_list_track_d_mentions_track_d(capsys) -> None:
    # Import and call the list command, then assert key UX strings are present.
    from pystatsv1.cli import main

    code = main(["workbook", "list", "--track", "d"])
    assert code == 0
    out = capsys.readouterr().out
    assert "run: d00_setup_data" in out
    assert "run: d00_peek_data" in out
    assert "run: d01" in out
    assert "run: d23" in out
