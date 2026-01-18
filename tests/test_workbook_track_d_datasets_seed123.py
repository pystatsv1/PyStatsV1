from __future__ import annotations

from argparse import Namespace
from pathlib import Path

import pystatsv1.cli as cli


def test_track_d_dataset_assets_exist() -> None:
    assets = Path("src") / "pystatsv1" / "assets"
    for name in (
        "ledgerlab_ch01_seed123.zip",
        "nso_v1_seed123.zip",
    ):
        assert (assets / name).exists(), f"Missing dataset asset: {assets / name}"


def test_workbook_init_track_d_extracts_seed123_datasets(tmp_path) -> None:
    dest = tmp_path / "wb_d"
    rc = cli.cmd_workbook_init(Namespace(track="d", dest=str(dest), force=False))
    assert rc == 0

    ledgerlab = dest / "data" / "synthetic" / "ledgerlab_ch01"
    nso = dest / "data" / "synthetic" / "nso_v1"

    assert (ledgerlab / "chart_of_accounts.csv").exists()
    assert (ledgerlab / "gl_journal.csv").exists()

    assert (nso / "chart_of_accounts.csv").exists()
    assert (nso / "gl_journal.csv").exists()
    assert (nso / "nso_v1_meta.json").exists()

    # quick sanity: non-empty core tables
    assert (ledgerlab / "gl_journal.csv").stat().st_size > 0
    assert (nso / "gl_journal.csv").stat().st_size > 0
