"""
Chapter 17 mixed-model (split-plot) design demo.

We simulate a Treatment vs Control study measured at three time points
(pre, post, followup), structure the data in wide/long format, and run
a mixed ANOVA using pingouin.mixed_anova.

Outputs:
- data/synthetic/psych_ch17_mixed_design_wide.csv
- data/synthetic/psych_ch17_mixed_design_long.csv
- outputs/track_b/ch17_mixed_anova.csv
- outputs/track_b/ch17_group_by_time_means.png
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pingouin as pg


DATA_DIR = Path("data") / "synthetic"
OUTPUT_DIR = Path("outputs") / "track_b"


@dataclass
class MixedDesignData:
    wide: pd.DataFrame
    long: pd.DataFrame


def simulate_mixed_design_dataset(
    n_per_group: int = 40,
    random_state: int | None = 123,
) -> MixedDesignData:
    """Simulate a 2(group) x 3(time) mixed design on anxiety scores.

    Design:
    - Between-subjects: group (control vs treatment)
    - Within-subjects: time (pre, post, followup)

    We engineer the means so that:
    - Both groups start similar at pre.
    - Treatment drops strongly at post and maintains gains at followup.
    - Control changes very little over time.
    """
    rng = np.random.default_rng(random_state)

    groups = ["control", "treatment"]
    times = ["pre", "post", "followup"]

    # Mean structure (rows = groups, cols = time)
    means = {
        "control": {"pre": 55.0, "post": 53.0, "followup": 52.0},
        "treatment": {"pre": 55.0, "post": 42.0, "followup": 40.0},
    }

    sd_within = 6.0  # within-person noise
    sd_between = 8.0  # between-person random intercept SD

    rows = []
    for group in groups:
        for i in range(n_per_group):
            subj_id = f"{group}_{i+1:02d}"
            # Random intercept: some people are generally higher/lower
            intercept = rng.normal(loc=0.0, scale=sd_between)
            for time in times:
                mu = means[group][time] + intercept
                score = rng.normal(loc=mu, scale=sd_within)
                rows.append(
                    {
                        "subject": subj_id,
                        "group": group,
                        "time": time,
                        "anxiety": score,
                    }
                )

    long_df = pd.DataFrame(rows)

    # Build wide format: one row per participant, columns per time
    wide_df = (
        long_df.pivot_table(
            index=["subject", "group"],
            columns="time",
            values="anxiety",
        )
        .reset_index()
        .rename_axis(None, axis=1)
    )

    wide_df = wide_df.rename(
        columns={
            "pre": "anxiety_pre",
            "post": "anxiety_post",
            "followup": "anxiety_followup",
        }
    )

    return MixedDesignData(wide=wide_df, long=long_df)


def run_mixed_anova(long_df: pd.DataFrame) -> pd.DataFrame:
    """Run mixed ANOVA with pingouin on long-format dataset.

    Factors:
    - between: group
    - within: time
    - dv: anxiety
    - subject: subject
    """
    aov = pg.mixed_anova(
        data=long_df,
        dv="anxiety",
        within="time",
        between="group",
        subject="subject",
    )
    return aov


def compute_group_time_means(long_df: pd.DataFrame) -> pd.DataFrame:
    """Compute mean anxiety for each group x time combination."""
    means = (
        long_df.groupby(["group", "time"], as_index=False)["anxiety"]
        .mean()
        .rename(columns={"anxiety": "mean_anxiety"})
    )
    return means


def plot_group_by_time_means(means_df: pd.DataFrame, output_path: Path) -> None:
    """Create a simple interaction plot of group means over time."""
    fig, ax = plt.subplots(figsize=(6, 4))

    times = ["pre", "post", "followup"]
    for group in sorted(means_df["group"].unique()):
        sub = means_df[means_df["group"] == group].set_index("time").loc[times]
        ax.plot(
            times,
            sub["mean_anxiety"],
            marker="o",
            label=group.capitalize(),
        )

    ax.set_xlabel("Time")
    ax.set_ylabel("Mean anxiety score")
    ax.set_title("Mixed design: Group × Time interaction (synthetic data)")
    ax.legend()
    fig.tight_layout()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def main() -> None:
    print("Simulating mixed-design dataset for Chapter 17...")

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    mixed = simulate_mixed_design_dataset()
    wide_df, long_df = mixed.wide, mixed.long

    print("\nFirst 6 rows (long format):")
    print(long_df.head(6))

    print("\nFirst 6 rows (wide format):")
    print(wide_df.head(6))

    aov = run_mixed_anova(long_df)
    print("\nPingouin mixed ANOVA (group × time) on anxiety scores")
    print("-" * 72)
    print(aov)

    means_df = compute_group_time_means(long_df)
    print("\nGroup × time means:")
    print(means_df)

    # Save outputs
    wide_path = DATA_DIR / "psych_ch17_mixed_design_wide.csv"
    long_path = DATA_DIR / "psych_ch17_mixed_design_long.csv"
    aov_path = OUTPUT_DIR / "ch17_mixed_anova.csv"
    fig_path = OUTPUT_DIR / "ch17_group_by_time_means.png"

    wide_df.to_csv(wide_path, index=False)
    long_df.to_csv(long_path, index=False)
    aov.to_csv(aov_path, index=False)
    plot_group_by_time_means(means_df, fig_path)

    print(f"\nWide data saved to: {wide_path}")
    print(f"Long data saved to: {long_path}")
    print(f"Mixed ANOVA table saved to: {aov_path}")
    print(f"Interaction plot saved to: {fig_path}")
    print("\nChapter 17 mixed-model lab complete.")


if __name__ == "__main__":
    main()
