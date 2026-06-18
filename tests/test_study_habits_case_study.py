from __future__ import annotations

from pathlib import Path

import pandas as pd

from scripts.study_habits_02_anova import run_anova


def test_study_habits_group_effect_is_present():
    # This dataset is designed for teaching: the group effect should be real and visible.
    path = Path("data") / "study_habits.csv"
    df = pd.read_csv(path)

    assert set(df["group"].unique()) == {"control", "flashcards", "spaced"}

    means = df.groupby("group")["posttest_score"].mean().to_dict()
    assert means["spaced"] > means["flashcards"] > means["control"]

    # Use the public lesson wrapper rather than raw Pingouin so this test follows
    # the same column-name compatibility path as the workbook script.
    aov = run_anova(df)
    assert "p-unc" in aov.columns

    p = float(aov.loc[aov["Source"] == "group", "p-unc"].iloc[0])
    assert p < 0.05
