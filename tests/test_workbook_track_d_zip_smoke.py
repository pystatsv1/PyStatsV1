from __future__ import annotations

import zipfile
from argparse import Namespace
from pathlib import Path

import pystatsv1.cli as cli


def test_workbook_track_d_zip_exists_and_has_expected_files() -> None:
    zip_path = Path("src") / "pystatsv1" / "assets" / "workbook_track_d.zip"
    assert zip_path.exists(), f"Missing Track D workbook zip at: {zip_path}"

    with zipfile.ZipFile(zip_path, "r") as z:
        names = set(z.namelist())

    expected = {
        "README.md",
        "Makefile",
        "scripts/d00_peek_data.py",
        "scripts/_cli.py",
        "scripts/_business_etl.py",
        "scripts/sim_business_nso_v1.py",
        "scripts/sim_business_ledgerlab.py",
        "scripts/business_ch01_accounting_measurement.py",
        "scripts/business_ch23_communicating_results_governance.py",
        "data/synthetic/.gitkeep",
        "data/synthetic/ledgerlab_ch01/.gitkeep",
        "data/synthetic/nso_v1/.gitkeep",
        "outputs/track_d/.gitkeep",
        "tests/test_business_smoke.py",
    }

    missing = expected - names
    assert not missing, f"missing from Track D starter zip: {sorted(missing)}"


def test_extract_workbook_template_track_d_extracts_scripts(tmp_path) -> None:
    dest = tmp_path / "wb_d"
    cli._extract_workbook_template(dest=dest, force=False, track="d")

    assert (dest / "scripts" / "business_ch01_accounting_measurement.py").exists()
    assert (dest / "scripts" / "d00_peek_data.py").exists()
    assert (dest / "outputs" / "track_d").exists()


def test_workbook_list_track_d_mentions_ch01(capsys) -> None:
    rc = cli.cmd_workbook_list(Namespace(track="d"))
    assert rc == 0
    out = capsys.readouterr().out
    assert "Ch01" in out
    assert "D00" in out
