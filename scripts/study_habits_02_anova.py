"""Study Habits Case Study — Part 2: One-way ANOVA.

Goal
----
Test whether the mean **posttest_score** differs across the three groups.

Run (Workbook):
    pystatsv1 workbook run study_habits_02_anova
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pingouin as pg

DATA_PATH = Path("data") / "study_habits.csv"
OUTPUT_DIR = Path("outputs") / "case_studies" / "study_habits"


def load_data(path: Path = DATA_PATH) -> pd.DataFrame:
    return pd.read_csv(path)


def run_anova(df: pd.DataFrame) -> pd.DataFrame:
    """One-way ANOVA on posttest_score by group."""
    return pg.anova(data=df, dv="posttest_score", between="group", detailed=True)


def main() -> int:
    df = load_data()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    aov = run_anova(df)
    out_csv = OUTPUT_DIR / "anova_posttest_by_group.csv"
    aov.to_csv(out_csv, index=False)

    print("\nOne-way ANOVA: posttest_score ~ group\n")
    print(aov.to_string(index=False))
    print("\nSaved: ", out_csv)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
