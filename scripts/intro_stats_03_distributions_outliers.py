"""Intro Stats case study — distributions + outliers.

Part 3 of the Intro Stats pack.

Creates:
  - outputs/case_studies/intro_stats/distributions_summary.csv
  - outputs/case_studies/intro_stats/outliers_iqr.csv
  - outputs/case_studies/intro_stats/score_distributions.png

Outlier rule used here (simple + teachable):
  - IQR rule *within each group*: [Q1 - 1.5*IQR, Q3 + 1.5*IQR]

This is not the only outlier rule, but it's easy to explain and visualize.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


# Matplotlib 3.9 renamed `labels` -> `tick_labels` for Axes.boxplot.
# This import works when run via `python -m scripts...` (package import),
# and also when run as a plain script from the `scripts/` folder.
try:
    from scripts._mpl_compat import ax_boxplot
except ImportError:  # pragma: no cover
    from _mpl_compat import ax_boxplot  # type: ignore


def _iqr_outliers(df: pd.DataFrame, *, group_col: str, value_col: str) -> pd.DataFrame:
    """Return a table of IQR outliers per group (may be empty)."""

    rows: list[dict[str, float | int | str]] = []

    for g, sub in df.groupby(group_col):
        s = sub[value_col].astype(float)
        q1 = float(s.quantile(0.25))
        q3 = float(s.quantile(0.75))
        iqr = q3 - q1
        low = q1 - 1.5 * iqr
        high = q3 + 1.5 * iqr

        mask = (s < low) | (s > high)
        if mask.any():
            flagged = sub.loc[mask, ["id", group_col, value_col]].copy()
            flagged["low"] = low
            flagged["high"] = high
            rows.extend(flagged.to_dict(orient="records"))

    out = pd.DataFrame(rows)
    if out.empty:
        # Still write a useful CSV with headers.
        out = pd.DataFrame(columns=["id", group_col, value_col, "low", "high"])
    return out


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    csv_path = root / "data" / "intro_stats_scores.csv"
    outdir = root / "outputs" / "case_studies" / "intro_stats"
    outdir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(csv_path)

    # --- Distribution summary (per group)
    dist = (
        df.groupby("group")["score"]
        .agg(
            n="size",
            mean="mean",
            std=lambda x: x.std(ddof=1),
            min="min",
            q1=lambda x: x.quantile(0.25),
            median="median",
            q3=lambda x: x.quantile(0.75),
            max="max",
        )
        .reset_index()
    )
    dist["iqr"] = dist["q3"] - dist["q1"]
    dist = dist[["group", "n", "mean", "std", "min", "q1", "median", "q3", "iqr", "max"]]
    dist.to_csv(outdir / "distributions_summary.csv", index=False)

    # --- Outliers (IQR rule)
    outliers = _iqr_outliers(df, group_col="group", value_col="score")
    outliers.to_csv(outdir / "outliers_iqr.csv", index=False)

    # --- Plot: histogram + boxplot
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))

    # Histograms
    for g, sub in df.groupby("group"):
        axes[0].hist(sub["score"], bins=10, alpha=0.6, label=str(g))
    axes[0].set_title("Score distributions")
    axes[0].set_xlabel("Score")
    axes[0].set_ylabel("Count")
    axes[0].legend()

    # Boxplot
    order = ["control", "treatment"]
    data = [df.loc[df["group"] == g, "score"] for g in order if g in set(df["group"])]
    tick_labels = [g for g in order if g in set(df["group"])]
    ax_boxplot(axes[1], data, tick_labels=tick_labels)
    axes[1].set_title("Boxplot (outliers shown)")
    axes[1].set_ylabel("Score")

    fig.tight_layout()
    fig.savefig(outdir / "score_distributions.png", dpi=150)
    plt.close(fig)

    print("Saved:", outdir / "distributions_summary.csv")
    print("Saved:", outdir / "outliers_iqr.csv")
    print("Saved:", outdir / "score_distributions.png")


if __name__ == "__main__":
    main()
