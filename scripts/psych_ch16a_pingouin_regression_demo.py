"""
Chapter 16a Pingouin regression appendix demo.

This script reuses the simulated regression dataset from Chapter 16 and
then leans on Pingouin to:

- Fit a multiple regression model with exam_score as the outcome
  and study_hours, sleep_hours, stress, and motivation as predictors.
- Compute standardized regression coefficients (betas) by running the
  same model on z-scored variables.
- Compute a partial correlation between exam_score and study_hours
  controlling for stress and motivation.

Artifacts:
- outputs/track_b/ch16a_regression_raw.csv
- outputs/track_b/ch16a_regression_standardized.csv
- outputs/track_b/ch16a_partial_corr_exam_study.csv
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd
import pingouin as pg

from scripts.psych_ch16_regression import simulate_psych_regression_dataset


TRACK_B_DIR = Path("outputs") / "track_b"
TRACK_B_DIR.mkdir(parents=True, exist_ok=True)


def zscore_columns(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    """Return a copy of df with z-scored versions of selected columns.

    Each z-scored column is added with a `_z` suffix.
    """
    zdf = df.copy()
    for col in columns:
        mean = zdf[col].mean()
        std = zdf[col].std(ddof=0)
        if std == 0:
            # Degenerate case; keep zeros so downstream code still works
            zdf[col + "_z"] = 0.0
        else:
            zdf[col + "_z"] = (zdf[col] - mean) / std
    return zdf


def build_pingouin_regression_tables(
    df: pd.DataFrame,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Fit raw and standardized multiple regression models with Pingouin.

    Returns
    -------
    raw_table : DataFrame
        Pingouin regression table on original-scale variables.
    standardized_table : DataFrame
        Pingouin regression table on z-scored predictors and outcome.
    """
    predictors = ["study_hours", "sleep_hours", "stress", "motivation"]
    outcome = "exam_score"

    X = df[predictors]
    y = df[outcome]

    raw_table = pg.linear_regression(X=X, y=y)

    zdf = zscore_columns(df, [outcome] + predictors)
    X_z = zdf[[p + "_z" for p in predictors]]
    y_z = zdf[outcome + "_z"]

    standardized_table = pg.linear_regression(X=X_z, y=y_z)

    return raw_table, standardized_table


def compute_partial_corr_exam_study(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Compute partial correlation exam_score ~ study_hours | stress, motivation."""
    partial = pg.partial_corr(
        data=df,
        x="study_hours",
        y="exam_score",
        covar=["stress", "motivation"],
        method="pearson",
    )
    return partial


def run_ch16a_demo(
    n: int = 250,
    random_state: int = 2025,
) -> Dict[str, pd.DataFrame]:
    """High-level driver for the Chapter 16a Pingouin regression appendix.

    Simulates data via the Chapter 16 helper, runs Pingouin regression,
    and writes CSV outputs.

    Returns
    -------
    results : dict
        Dictionary with keys:
        - "df"
        - "raw_table"
        - "standardized_table"
        - "partial_corr"
    """
    print("Simulating psychology regression dataset for Chapter 16a appendix...")
    df = simulate_psych_regression_dataset(n=n, random_state=random_state)

    print("\nFirst 5 rows of the dataset:")
    print(df.head())

    print("\nFitting Pingouin multiple regression:")
    raw_table, standardized_table = build_pingouin_regression_tables(df)
    print("\nRaw-scale regression table:")
    print(raw_table)

    print("\nStandardized regression table (betas):")
    print(standardized_table)

    print("\nComputing partial correlation:")
    partial = compute_partial_corr_exam_study(df)
    print("\nPartial correlation exam_score ~ study_hours | stress, motivation:")
    print(partial)

    raw_path = TRACK_B_DIR / "ch16a_regression_raw.csv"
    std_path = TRACK_B_DIR / "ch16a_regression_standardized.csv"
    partial_path = TRACK_B_DIR / "ch16a_partial_corr_exam_study.csv"

    raw_table.to_csv(raw_path, index=False)
    standardized_table.to_csv(std_path, index=False)
    partial.to_csv(partial_path, index=False)

    print(f"\nRaw regression table saved to: {raw_path}")
    print(f"Standardized regression table saved to: {std_path}")
    print(f"Partial correlation table saved to: {partial_path}")

    print("\nChapter 16a Pingouin regression appendix demo complete.")

    return {
        "df": df,
        "raw_table": raw_table,
        "standardized_table": standardized_table,
        "partial_corr": partial,
    }


def main() -> None:
    run_ch16a_demo()


if __name__ == "__main__":
    main()
