"""
Chapter 14a Pingouin appendix demo:
Repeated-measures ANOVA using pingouin.rm_anova.

This script has two main purposes:

1. Provide reusable helpers for the tests and textbook:
   - simulate_repeated_measures_data
   - run_pingouin_rm_anova

2. Act as a CLI demo when run as a module:
   python -m scripts.psych_ch14a_pingouin_rm_demo
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import pingouin as pg


def simulate_repeated_measures_data(
    n_subjects: int = 40,
    seed: Optional[int] = 123,
) -> pd.DataFrame:
    """Simulate a simple 3-timepoint repeated-measures dataset.

    Columns:
    - subject: integer id (1..n_subjects)
    - time: 'pre', 'post', 'followup'
    - stress_score: continuous outcome
    """
    if seed is not None:
        np.random.seed(seed)

    subjects = np.arange(1, n_subjects + 1)
    times = ["pre", "post", "followup"]

    rows = []
    for s in subjects:
        # Subject-specific baseline
        baseline = np.random.normal(loc=20.0, scale=4.0)

        # Time-specific means: stress decreases over time
        means = {
            "pre": baseline,
            "post": baseline - 4.0,
            "followup": baseline - 7.0,
        }

        for t in times:
            score = np.random.normal(loc=means[t], scale=2.5)
            rows.append({"subject": s, "time": t, "stress_score": score})

    df_long = pd.DataFrame(rows)
    return df_long


def run_pingouin_rm_anova(df_long: pd.DataFrame) -> pd.DataFrame:
    """Run pingouin.rm_anova on the long-format repeated-measures data.

    Returns the ANOVA table as a pandas DataFrame.
    """
    anova_table = pg.rm_anova(
        dv="stress_score",
        within="time",
        subject="subject",
        data=df_long,
        detailed=True,
    )
    return anova_table


def main() -> None:
    """CLI entry point for the Appendix 14a repeated-measures demo."""
    df_long = simulate_repeated_measures_data()

    print("First 6 rows of the long-format data:")
    print(df_long.head(6))
    print()

    print("Pingouin repeated-measures ANOVA on Time (pre, post, followup)")
    print("------------------------------------------------------------------------")
    anova_table = run_pingouin_rm_anova(df_long)
    print(anova_table)
    print()

    # Save data and ANOVA table to disk (mirrors Chapter 14 style)
    data_path = Path("data") / "synthetic"
    data_path.mkdir(parents=True, exist_ok=True)
    outputs_path = Path("outputs") / "track_b"
    outputs_path.mkdir(parents=True, exist_ok=True)

    df_long.to_csv(
        data_path / "psych_ch14a_pingouin_rm_demo.csv",
        index=False,
    )
    anova_table.to_csv(
        outputs_path / "ch14a_pingouin_rm_anova.csv",
        index=False,
    )

    print(f"Data saved to: {data_path / 'psych_ch14a_pingouin_rm_demo.csv'}")
    print(
        "Pingouin ANOVA table saved to: "
        f"{outputs_path / 'ch14a_pingouin_rm_anova.csv'}"
    )


if __name__ == "__main__":
    main()
