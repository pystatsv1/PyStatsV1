from __future__ import annotations

import re
import zipfile
from pathlib import Path


def test_workbook_starter_zip_includes_case_study_packs_and_my_data_template() -> None:
    zip_path = Path("src") / "pystatsv1" / "assets" / "workbook_starter.zip"
    assert zip_path.exists(), f"Missing starter zip at: {zip_path}"

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

        # Intro Stats pack (full 5-pack)
        "data/intro_stats_scores.csv",
        "scripts/intro_stats_01_descriptives.py",
        "scripts/intro_stats_02_simulation.py",
        "scripts/intro_stats_03_distributions_outliers.py",
        "scripts/intro_stats_04_confidence_intervals.py",
        "scripts/intro_stats_05_hypothesis_testing.py",
        "writeups/intro_stats_interpretation_template.md",
        "tests/test_intro_stats_case_study.py",
    }

    missing = expected - names
    assert not missing, f"missing from starter zip: {sorted(missing)}"


def test_workbook_starter_zip_intro_stats_dataset_matches_test_contract() -> None:
    """The starter ZIP must not ship an inconsistent dataset/test pair.

    Regression: we once shipped intro_stats_scores.csv with 40 rows but a test
    asserting len(df) == 60, causing fresh installs to fail on `workbook check`.
    """

    zip_path = Path("src") / "pystatsv1" / "assets" / "workbook_starter.zip"
    assert zip_path.exists(), f"Missing starter zip at: {zip_path}"

    with zipfile.ZipFile(zip_path, "r") as z:
        csv_text = z.read("data/intro_stats_scores.csv").decode("utf-8").strip().splitlines()
        test_text = z.read("tests/test_intro_stats_case_study.py").decode("utf-8")

    # CSV row count excluding header
    assert csv_text, "intro_stats_scores.csv is empty"
    n_rows = len(csv_text) - 1

    m = re.search(r"assert\s+len\(df\)\s*==\s*(\d+)", test_text)
    assert m, "Could not find a len(df)==N assertion in starter test_intro_stats_case_study.py"
    expected_n = int(m.group(1))

    assert expected_n == n_rows, (
        "Starter ZIP intro stats contract mismatch: "
        f"data has {n_rows} rows but test asserts len(df)=={expected_n}. "
        "Regenerate src/pystatsv1/assets/workbook_starter.zip."
    )
