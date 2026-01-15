from __future__ import annotations

import zipfile
from pathlib import Path


def test_workbook_starter_zip_includes_study_habits_pack():
    zip_path = Path("src") / "pystatsv1" / "assets" / "workbook_starter.zip"
    assert zip_path.exists()

    with zipfile.ZipFile(zip_path, "r") as z:
        names = set(z.namelist())

    expected = {
        "data/study_habits.csv",
        "scripts/study_habits_01_explore.py",
        "scripts/study_habits_02_anova.py",
        "tests/test_study_habits_case_study.py",
    }
    missing = expected - names
    assert not missing, f"missing from starter zip: {sorted(missing)}"
