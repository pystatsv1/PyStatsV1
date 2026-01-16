"""Intro Stats case study — confidence intervals.

Part 4 of the Intro Stats pack.

Goal:
  - Build intuition for uncertainty around an average.

Creates:
  - outputs/case_studies/intro_stats/ci_group_means_95.csv
  - outputs/case_studies/intro_stats/ci_mean_diff_welch_95.csv
  - outputs/case_studies/intro_stats/ci_group_means_95.png

Notes:
  - We use a simple t-based 95% CI for each group mean.
  - For the mean difference, we use a Welch-style CI (no equal-variance assumption).
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats


def _ci_mean_t(s: pd.Series, alpha: float = 0.05) -> tuple[float, float, float]:
    """Return (mean, lo, hi) for a t-based CI."""
    n = int(s.size)
    mean = float(s.mean())
    sd = float(s.std(ddof=1))
    se = sd / np.sqrt(n)
    df = n - 1
    tcrit = float(stats.t.ppf(1 - alpha / 2, df))
    lo = mean - tcrit * se
    hi = mean + tcrit * se
    return mean, lo, hi


def _ci_mean_diff_welch(
    s_treat: pd.Series, s_control: pd.Series, alpha: float = 0.05
) -> tuple[float, float, float, float]:
    """Return (diff, lo, hi, df_welch) for Welch CI on mean difference."""
    n1 = float(s_treat.size)
    n0 = float(s_control.size)
    m1 = float(s_treat.mean())
    m0 = float(s_control.mean())
    v1 = float(s_treat.var(ddof=1))
    v0 = float(s_control.var(ddof=1))

    diff = m1 - m0
    se2 = v1 / n1 + v0 / n0
    se = float(np.sqrt(se2))

    # Welch–Satterthwaite df
    num = se2**2
    den = (v1**2) / (n1**2 * (n1 - 1)) + (v0**2) / (n0**2 * (n0 - 1))
    df = float(num / den)

    tcrit = float(stats.t.ppf(1 - alpha / 2, df))
    lo = diff - tcrit * se
    hi = diff + tcrit * se
    return diff, lo, hi, df


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    csv_path = root / "data" / "intro_stats_scores.csv"
    outdir = root / "outputs" / "case_studies" / "intro_stats"
    outdir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(csv_path)

    rows: list[dict[str, float | str]] = []
    for g, sub in df.groupby("group"):
        mean, lo, hi = _ci_mean_t(sub["score"], alpha=0.05)
        rows.append({"group": str(g), "mean": mean, "ci_lo": lo, "ci_hi": hi})

    ci_means = pd.DataFrame(rows).sort_values("group")
    ci_means.to_csv(outdir / "ci_group_means_95.csv", index=False)

    s_control = df.loc[df["group"] == "control", "score"]
    s_treat = df.loc[df["group"] == "treatment", "score"]

    diff, lo, hi, df_welch = _ci_mean_diff_welch(s_treat, s_control, alpha=0.05)
    ci_diff = pd.DataFrame(
        [
            {
                "contrast": "treatment - control",
                "mean_diff": diff,
                "ci_lo": lo,
                "ci_hi": hi,
                "df_welch": df_welch,
            }
        ]
    )
    ci_diff.to_csv(outdir / "ci_mean_diff_welch_95.csv", index=False)

    # Plot: group means with CI
    fig, ax = plt.subplots(figsize=(6, 4))
    x = np.arange(ci_means.shape[0])
    y = ci_means["mean"].to_numpy()
    yerr = np.vstack([y - ci_means["ci_lo"].to_numpy(), ci_means["ci_hi"].to_numpy() - y])

    ax.errorbar(x, y, yerr=yerr, fmt="o", capsize=6)
    ax.set_xticks(x)
    ax.set_xticklabels(ci_means["group"].tolist())
    ax.set_ylabel("Score")
    ax.set_title("95% CI for each group mean")
    fig.tight_layout()
    fig.savefig(outdir / "ci_group_means_95.png", dpi=150)
    plt.close(fig)

    print("Saved:", outdir / "ci_group_means_95.csv")
    print("Saved:", outdir / "ci_mean_diff_welch_95.csv")
    print("Saved:", outdir / "ci_group_means_95.png")


if __name__ == "__main__":
    main()
