"""Study Habits Case Study — Part 1: Explore the data.

Story (short version)
---------------------
A school is testing three study strategies over 4 weeks:

* control      — "study like you normally do"
* flashcards   — daily flashcard practice
* spaced       — spaced repetition schedule

You will explore the dataset and generate a few starter outputs you can inspect.

Run (Workbook):
    pystatsv1 workbook run study_habits_01_explore
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

DATA_PATH = Path("data") / "study_habits.csv"
OUTPUT_DIR = Path("outputs") / "case_studies" / "study_habits"


def load_data(path: Path = DATA_PATH) -> pd.DataFrame:
    """Load the Study Habits dataset from CSV."""
    return pd.read_csv(path)


def group_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Compute a simple summary table by group."""
    cols = ["pretest_score", "posttest_score", "retention_score", "study_hours_per_week"]
    return df.groupby("group", as_index=False)[cols].agg(["count", "mean", "std"]).reset_index(drop=True)


def main() -> int:
    df = load_data()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("\nStudy Habits — head()\n")
    print(df.head(10).to_string(index=False))

    print("\nGroup sizes\n")
    print(df["group"].value_counts().to_string())

    summary = (
        df.groupby("group", as_index=False)
        .agg(
            n=("student_id", "count"),
            pre_mean=("pretest_score", "mean"),
            post_mean=("posttest_score", "mean"),
            retention_mean=("retention_score", "mean"),
            hours_mean=("study_hours_per_week", "mean"),
        )
        .sort_values("post_mean", ascending=False)
    )

    out_csv = OUTPUT_DIR / "group_summary.csv"
    summary.to_csv(out_csv, index=False)

    print("\nSaved: ", out_csv)
    print(summary.to_string(index=False, float_format=lambda x: f"{x:0.2f}"))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
