"""Regression tests for Pingouin compatibility helpers in the workbook starter ZIP."""

from __future__ import annotations

from pathlib import Path
from zipfile import ZipFile


def test_workbook_starter_zip_includes_pingouin_compat_helper() -> None:
    zip_path = Path("src") / "pystatsv1" / "assets" / "workbook_starter.zip"
    assert zip_path.exists(), f"Missing starter zip at: {zip_path}"

    with ZipFile(zip_path) as zf:
        names = set(zf.namelist())
        assert "scripts/_pingouin_compat.py" in names
        ch10 = zf.read("scripts/psych_ch10_problem_set.py").decode("utf-8")

    assert "add_pingouin_legacy_aliases" in ch10
    assert "p-val" in ch10
