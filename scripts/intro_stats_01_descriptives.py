"""Intro Stats case study pack (Part 1): descriptives.

This script is designed for absolute beginners. It demonstrates the workbook
pattern: Run → Inspect → Check.

It reads a tiny dataset from data/intro_stats_scores.csv and produces:

- a group summary table (CSV)
- a quick plot (PNG)

Outputs are written under outputs/case_studies/intro_stats/.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    csv_path = root / "data" / "intro_stats_scores.csv"
    outdir = root / "outputs" / "case_studies" / "intro_stats"
    outdir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(csv_path)

    print("Intro Stats — head()\n")
    print(df.head(10).to_string(index=False))
    print()

    print("Group sizes\n")
    print(df["group"].value_counts().to_string())
    print()

    # Group summary (beginner-friendly)
    summary = (
        df.groupby("group")
        .agg(
            n=("score", "size"),
            mean=("score", "mean"),
            median=("score", "median"),
            sd=("score", "std"),
            min=("score", "min"),
            max=("score", "max"),
        )
        .reset_index()
        .sort_values("group")
    )

    out_csv = outdir / "group_summary.csv"
    summary.to_csv(out_csv, index=False)

    print("Saved:", out_csv)
    print(summary.to_string(index=False))

    # A quick plot (boxplot) — optional, but helpful visually.
    try:
        import matplotlib.pyplot as plt

        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)

        # Keep ordering stable.
        order = ["control", "treatment"]
        data = [df.loc[df["group"] == g, "score"].to_numpy() for g in order]
        ax.boxplot(data, labels=order)
        ax.set_title("Intro Stats: score by group")
        ax.set_ylabel("score")

        out_png = outdir / "score_by_group.png"
        fig.tight_layout()
        fig.savefig(out_png, dpi=150)
        plt.close(fig)
        print("Saved:", out_png)
    except Exception as e:  # pragma: no cover
        print("(Plot skipped)")
        print("Reason:", e)


if __name__ == "__main__":
    main()
