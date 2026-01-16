"""Intro Stats case study — hypothesis testing by simulation + effect size.

Part 5 of the Intro Stats pack.

Goal:
  - Learn a *randomization / permutation test* intuition for p-values.
  - Compute a simple standardized effect size (Cohen's d) for the group difference.

Creates:
  - outputs/case_studies/intro_stats/permutation_test_summary.csv
  - outputs/case_studies/intro_stats/effect_size.csv
  - outputs/case_studies/intro_stats/permutation_distribution.png

How the permutation test works:
  1) Compute the observed mean difference (treatment - control).
  2) Shuffle group labels many times and recompute the mean difference.
  3) The p-value is the fraction of shuffles with |diff| >= |observed|.

This is a great "first hypothesis test" because it requires almost no formulas.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def _cohens_d(x: np.ndarray, y: np.ndarray) -> float:
    """Cohen's d for difference in means (x - y) using pooled SD."""
    nx = x.size
    ny = y.size
    sx2 = x.var(ddof=1)
    sy2 = y.var(ddof=1)
    sp2 = ((nx - 1) * sx2 + (ny - 1) * sy2) / (nx + ny - 2)
    sp = float(np.sqrt(sp2))
    if sp == 0:
        return float("nan")
    return float((x.mean() - y.mean()) / sp)


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    csv_path = root / "data" / "intro_stats_scores.csv"
    outdir = root / "outputs" / "case_studies" / "intro_stats"
    outdir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(csv_path)

    control = df.loc[df["group"] == "control", "score"].to_numpy(dtype=float)
    treat = df.loc[df["group"] == "treatment", "score"].to_numpy(dtype=float)

    obs_diff = float(treat.mean() - control.mean())

    # Permutation test: shuffle labels, keep group sizes fixed.
    n_perm = 5000
    seed = 20260115
    rng = np.random.default_rng(seed)

    all_scores = np.concatenate([control, treat])
    n0 = control.size
    n1 = treat.size

    perm_diffs = np.empty(n_perm, dtype=float)
    for i in range(n_perm):
        perm = rng.permutation(all_scores)
        perm_control = perm[:n0]
        perm_treat = perm[n0 : n0 + n1]
        perm_diffs[i] = perm_treat.mean() - perm_control.mean()

    more_extreme = int(np.sum(np.abs(perm_diffs) >= abs(obs_diff)))
    p_two_sided = float((more_extreme + 1) / (n_perm + 1))

    summary = pd.DataFrame(
        [
            {
                "observed_mean_diff": obs_diff,
                "p_value_two_sided": p_two_sided,
                "more_extreme": more_extreme,
                "n_perm": n_perm,
                "seed": seed,
                "note": "permutation test on mean difference (treatment - control)",
            }
        ]
    )
    summary.to_csv(outdir / "permutation_test_summary.csv", index=False)

    d = _cohens_d(treat, control)
    # Small-sample bias correction (Hedges' g) is optional, but it's a nice extra.
    j = 1.0 - 3.0 / (4.0 * (n0 + n1) - 9.0)
    g = float(j * d)

    eff = pd.DataFrame(
        [
            {
                "effect": "treatment - control",
                "cohens_d": d,
                "hedges_g": g,
                "interpretation_hint": "~0.2 small, ~0.5 medium, ~0.8 large (very rough)",
            }
        ]
    )
    eff.to_csv(outdir / "effect_size.csv", index=False)

    # Plot the permutation distribution.
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(perm_diffs, bins=40)
    ax.axvline(obs_diff, linestyle="--")
    ax.axvline(-obs_diff, linestyle=":")
    ax.set_title("Permutation distribution of mean differences")
    ax.set_xlabel("Mean difference (treatment - control)")
    ax.set_ylabel("Count")
    fig.tight_layout()
    fig.savefig(outdir / "permutation_distribution.png", dpi=150)
    plt.close(fig)

    print("Observed mean diff (treatment - control):", round(obs_diff, 3))
    print("Permutation p-value (two-sided):", round(p_two_sided, 4))
    print("Saved:", outdir / "permutation_test_summary.csv")
    print("Saved:", outdir / "effect_size.csv")
    print("Saved:", outdir / "permutation_distribution.png")


if __name__ == "__main__":
    main()
