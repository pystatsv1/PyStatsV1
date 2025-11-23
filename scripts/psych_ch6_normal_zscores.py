# SPDX-License-Identifier: MIT
"""Chapter 6 helper: normal distribution & z-scores for the sleep-study data."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from scripts.sim_psych_sleep_study import load_sleep_study

# You can tweak this if you prefer reaction time, etc.
DEFAULT_VAR = "sleep_hours"


def compute_zscores(series: pd.Series) -> pd.Series:
    """Return z-scores using sample mean and sample standard deviation."""
    mean = series.mean()
    sd = series.std(ddof=1)
    return (series - mean) / sd


def summarize_tails(z: pd.Series) -> dict[str, float]:
    """Return proportions of |z| > 2 and |z| > 3."""
    abs_z = z.abs()
    return {
        "prop_gt_2": float((abs_z > 2).mean()),
        "prop_gt_3": float((abs_z > 3).mean()),
    }


def make_hist_with_normal(series: pd.Series, out_path: Path) -> Path:
    """Plot histogram with a fitted normal density overlay."""
    mean = series.mean()
    sd = series.std(ddof=1)

    fig, ax = plt.subplots()
    ax.hist(series, bins=20, density=True, alpha=0.7)
    x = np.linspace(series.min(), series.max(), 200)
    y = (1 / (sd * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - mean) / sd) ** 2)
    ax.plot(x, y)
    ax.set_xlabel(series.name)
    ax.set_ylabel("Density")
    ax.set_title(f"{series.name}: histogram with normal curve")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    return out_path


def main(
    csv_path: Path = Path("data/synthetic/psych_sleep_study.csv"),
    out_plot: Path = Path("outputs/track_b/ch06_sleep_hours_hist.png"),
    var: str = DEFAULT_VAR,
) -> int:
    df = load_sleep_study(path=csv_path)
    series = df[var].astype(float)
    z = compute_zscores(series)
    tails = summarize_tails(z)

    print(f"Variable: {var}")
    print(f"Mean: {series.mean():.2f}")
    print(f"SD:   {series.std(ddof=1):.2f}")
    print(f"Proportion |z| > 2: {tails['prop_gt_2']:.3f}")
    print(f"Proportion |z| > 3: {tails['prop_gt_3']:.3f}")

    make_hist_with_normal(series, out_plot)
    print(f"Wrote plot to: {out_plot}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
