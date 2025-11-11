# SPDX-License-Identifier: MIT
"""
Chapter 14: Two-Sample (Welch's) t-test
Education Case Study: Control vs. Tutoring Group

Loads the simulated data, runs a t-test, calculates Cohen's d,
and saves a summary JSON and a boxplot.
"""

from __future__ import annotations

import json
import pathlib
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np
import pandas as pd
from scipy import stats

from scripts._cli import base_parser, apply_seed


def cohens_d(x: np.ndarray, y: np.ndarray) -> float:
    """Cohen's d for independent samples using pooled SD."""
    n1, n2 = len(x), len(y)
    s1 = float(np.std(x, ddof=1))
    s2 = float(np.std(y, ddof=1))
    m1 = float(np.mean(x))
    m2 = float(np.mean(y))
    s_pooled = np.sqrt(((n1 - 1) * s1**2 + (n2 - 1) * s2**2) / (n1 + n2 - 2))
    return (m2 - m1) / s_pooled


def main() -> None:
    parser = base_parser("Chapter 14 Analyzer: A/B Tutoring Study (Welch's t-test)")
    parser.add_argument(
        "--datadir",
        type=pathlib.Path,
        default=pathlib.Path("data/synthetic"),
        help="Directory to read simulated data from",
    )
    args = parser.parse_args()

    # Setup
    apply_seed(args.seed)
    args.outdir.mkdir(parents=True, exist_ok=True)

    data_file = args.datadir / "ch14_tutoring_data.csv"
    if not data_file.exists():
        print(f"Data not found: {data_file}")
        print("Hint: run `python -m scripts.sim_ch14_tutoring --outdir data/synthetic`.")
        return

    # Load
    df = pd.read_csv(data_file)
    control = df.loc[df["group"] == "Control", "score"].to_numpy()
    tutor = df.loc[df["group"] == "Tutor", "score"].to_numpy()

    print(f"Loaded {df.shape[0]} rows from {data_file}")
    print(
        f"Control  n={len(control)}  mean={control.mean():.2f}  sd={control.std(ddof=1):.2f}"
    )
    print(
        f"Tutor    n={len(tutor)}    mean={tutor.mean():.2f}    sd={tutor.std(ddof=1):.2f}"
    )

    # Welch's t-test (robust to unequal variances)
    t_res = stats.ttest_ind(tutor, control, equal_var=False)
    d_val = cohens_d(control, tutor)

    print("\n--- Welch's t-test: Tutor vs Control ---")
    print(f"t = {t_res.statistic:.4f}, p = {t_res.pvalue:.4f}, Cohen's d = {d_val:.4f}")

    # Summary JSON
    summary: dict[str, Any] = {
        "test_type": "Welch t-test",
        "comparison": "Tutor vs Control",
        "control_n": int(len(control)),
        "control_mean": float(control.mean()),
        "control_sd": float(control.std(ddof=1)),
        "tutor_n": int(len(tutor)),
        "tutor_mean": float(tutor.mean()),
        "tutor_sd": float(tutor.std(ddof=1)),
        "t_statistic": float(t_res.statistic),
        "p_value": float(t_res.pvalue),
        "cohens_d": float(d_val),
    }
    summary_path = args.outdir / "ch14_tutoring_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"Wrote summary → {summary_path}")

    # Plot
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.boxplot([control, tutor], labels=["Control", "Tutor"], patch_artist=True)
    ax.set_title(f"Test Scores: Control vs Tutor (n={len(control)} per group)")
    ax.set_ylabel("Score")
    ax.grid(axis="y", linestyle=":", alpha=0.7)
    plot_path = args.outdir / "ch14_tutoring_boxplot.png"
    fig.tight_layout()
    fig.savefig(plot_path, dpi=150)
    print(f"Wrote plot → {plot_path}")


if __name__ == "__main__":
    main()
