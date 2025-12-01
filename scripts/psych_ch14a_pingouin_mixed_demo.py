"""
Chapter 14a Pingouin appendix demo:
Mixed (split-plot) ANOVA using pingouin.mixed_anova.

Helpers:
- simulate_mixed_design_data
- run_pingouin_mixed_anova

CLI:
python -m scripts.psych_ch14a_pingouin_mixed_demo
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import pingouin as pg


def simulate_mixed_design_data(
    n_per_group: int = 20,
    seed: Optional[int] = 123,
) -> pd.DataFrame:
    """Simulate a simple mixed design with:

    - Between-subjects factor: group (control vs treatment)
    - Within-subjects factor: time (pre vs post)
    - Outcome: stress_score

    Returns a long-format DataFrame with columns:
    - subject (string label, e.g. 'control_01')
    - group ('control' or 'treatment')
    - time ('pre', 'post')
    - stress_score (continuous)
    """
    if seed is not None:
        np.random.seed(seed)

    groups = ["control", "treatment"]
    times = ["pre", "post"]

    rows = []
    for g in groups:
        for i in range(1, n_per_group + 1):
            subject_label = f"{g}_{i:02d}"

            # Subject-specific baseline
            baseline = np.random.normal(loc=20.0, scale=4.0)

            for t in times:
                if g == "control":
                    # Control: small change over time
                    mean = baseline if t == "pre" else baseline - 2.0
                else:
                    # Treatment: larger improvement by post
                    mean = baseline if t == "pre" else baseline - 6.0

                score = np.random.normal(loc=mean, scale=2.5)

                rows.append(
                    {
                        "subject": subject_label,
                        "group": g,
                        "time": t,
                        "stress_score": score,
                    }
                )

    df_long = pd.DataFrame(rows)
    return df_long


def run_pingouin_mixed_anova(df_long: pd.DataFrame) -> pd.DataFrame:
    """Run pingouin.mixed_anova on the mixed-design dataset.

    Returns the ANOVA table as a pandas DataFrame.
    """
    anova_table = pg.mixed_anova(
        dv="stress_score",
        within="time",
        between="group",
        subject="subject",
        data=df_long,
        effsize="np2",
    )
    return anova_table


def main() -> None:
    """CLI entry point for the Appendix 14a mixed-design demo."""
    df_long = simulate_mixed_design_data()

    print("First 8 rows of the mixed-design long-format data:")
    print(df_long.head(8))
    print()

    print("Pingouin mixed ANOVA (group × time) on stress scores")
    print("------------------------------------------------------------------------")
    anova_table = run_pingouin_mixed_anova(df_long)
    print(anova_table)
    print()

    # Save data and ANOVA table
    data_path = Path("data") / "synthetic"
    data_path.mkdir(parents=True, exist_ok=True)
    outputs_path = Path("outputs") / "track_b"
    outputs_path.mkdir(parents=True, exist_ok=True)

    df_long.to_csv(
        data_path / "psych_ch14a_pingouin_mixed_demo.csv",
        index=False,
    )
    anova_table.to_csv(
        outputs_path / "ch14a_pingouin_mixed_anova.csv",
        index=False,
    )

    print(
        f"Data saved to: {data_path / 'psych_ch14a_pingouin_mixed_demo.csv'}"
    )
    print(
        "Pingouin mixed ANOVA table saved to: "
        f"{outputs_path / 'ch14a_pingouin_mixed_anova.csv'}"
    )


if __name__ == "__main__":
    main()
