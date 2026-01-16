from __future__ import annotations

import zipfile
from pathlib import Path


def test_workbook_starter_zip_includes_case_study_packs_and_my_data_template() -> None:
    zip_path = Path("src") / "pystatsv1" / "assets" / "workbook_starter.zip"
    assert zip_path.exists()

    with zipfile.ZipFile(zip_path, "r") as z:
        names = set(z.namelist())

    expected = {
        # Study Habits pack
        "data/study_habits.csv",
        "scripts/study_habits_01_explore.py",
        "scripts/study_habits_02_anova.py",
        "tests/test_study_habits_case_study.py",

        # My Own Data mini-guide template
        "data/my_data.csv",
        "scripts/my_data_01_explore.py",
        "tests/test_my_data.py",

        # Intro Stats pack
        "data/intro_stats_scores.csv",
        "scripts/intro_stats_01_descriptives.py",
        "scripts/intro_stats_02_simulation.py",
        "tests/test_intro_stats_case_study.py",
    }
    missing = expected - names
    assert not missing, f"missing from starter zip: {sorted(missing)}"
