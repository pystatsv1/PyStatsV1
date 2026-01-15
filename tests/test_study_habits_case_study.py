from __future__ import annotations

from pathlib import Path

import pandas as pd
import pingouin as pg


def test_study_habits_group_effect_is_present():
    # This dataset is designed for teaching: the group effect should be real and visible.
    path = Path("data") / "study_habits.csv"
    df = pd.read_csv(path)

    assert set(df["group"].unique()) == {"control", "flashcards", "spaced"}

    means = df.groupby("group")["posttest_score"].mean().to_dict()
    assert means["spaced"] > means["flashcards"] > means["control"]

    aov = pg.anova(data=df, dv="posttest_score", between="group", detailed=True)
    p = float(aov.loc[aov["Source"] == "group", "p-unc"].iloc[0])
    assert p < 0.05
