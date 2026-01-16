"""Intro Stats 5 — Permutation test (simulation) + effect sizes.

Runs a permutation test for the difference in means (treatment minus control)
and computes two standardized effect sizes (Cohen's d and Hedges' g).

Outputs
-------
Written under outputs/case_studies/intro_stats/

- permutation_test_summary.csv
- effect_size.csv
- permutation_null_distribution.png
- permutation_dist.png (alias for the same plot; used by some docs)

The simulation uses a fixed random seed by default to keep the outputs
reproducible.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


DEFAULT_CSV = Path("data") / "intro_stats_scores.csv"
DEFAULT_OUTDIR = Path("outputs") / "case_studies" / "intro_stats"


def _cohen_d(control: np.ndarray, treatment: np.ndarray) -> float:
    n1 = len(control)
    n2 = len(treatment)
    s1 = np.var(control, ddof=1)
    s2 = np.var(treatment, ddof=1)
    sp = np.sqrt(((n1 - 1) * s1 + (n2 - 1) * s2) / (n1 + n2 - 2))
    if sp == 0:
        return float("nan")
    return (np.mean(treatment) - np.mean(control)) / sp


def _hedges_g(d: float, n1: int, n2: int) -> float:
    # Small sample correction.
    df = n1 + n2 - 2
    if df <= 1:
        return float("nan")
    j = 1 - (3 / (4 * df - 1))
    return d * j


def _permutation_distribution(
    scores: np.ndarray,
    labels: np.ndarray,
    n_perm: int,
    seed: int,
) -> np.ndarray:
    rng = np.random.default_rng(seed)
    diffs = np.empty(n_perm, dtype=float)
    for i in range(n_perm):
        perm_labels = rng.permutation(labels)
        diffs[i] = scores[perm_labels == 1].mean() - scores[perm_labels == 0].mean()
    return diffs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--outdir", type=Path, default=DEFAULT_OUTDIR)
    parser.add_argument("--n-perm", type=int, default=10_000)
    parser.add_argument("--seed", type=int, default=123)
    args = parser.parse_args()

    args.outdir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(args.csv)
    if set(df.columns) != {"id", "group", "score"}:
        raise SystemExit("Expected columns: id, group, score")

    control = df.loc[df["group"] == "control", "score"].to_numpy(dtype=float)
    treatment = df.loc[df["group"] == "treatment", "score"].to_numpy(dtype=float)
    if len(control) == 0 or len(treatment) == 0:
        raise SystemExit("Expected groups: control and treatment")

    observed = float(treatment.mean() - control.mean())

    # Encode labels so permutation is fast.
    scores = df["score"].to_numpy(dtype=float)
    labels = (df["group"].to_numpy() == "treatment").astype(int)

    perm_diffs = _permutation_distribution(scores, labels, n_perm=args.n_perm, seed=args.seed)

    # Two-sided p-value.
    p_value = float((np.abs(perm_diffs) >= abs(observed)).mean())

    # Outputs: summary table
    summary = pd.DataFrame(
        {
            "observed_mean_diff": [observed],
            "p_value_two_sided": [p_value],
            "n_perm": [args.n_perm],
            "seed": [args.seed],
        }
    )
    out_summary = args.outdir / "permutation_test_summary.csv"
    summary.to_csv(out_summary, index=False)

    # Outputs: effect sizes
    d = _cohen_d(control, treatment)
    g = _hedges_g(d, n1=len(control), n2=len(treatment))
    effect = pd.DataFrame(
        {
            "mean_diff": [observed],
            "cohen_d": [d],
            "hedges_g": [g],
        }
    )
    out_effect = args.outdir / "effect_size.csv"
    effect.to_csv(out_effect, index=False)

    # Outputs: plot (save under both names used in docs)
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.hist(perm_diffs, bins=40, alpha=0.8)
    ax.axvline(0.0, linestyle="--", linewidth=1.5)
    ax.axvline(observed, linestyle="-", linewidth=2)
    ax.set_title("Permutation null distribution: mean difference (treatment - control)")
    ax.set_xlabel("Mean difference")
    ax.set_ylabel("Count")
    fig.tight_layout()

    out_png_primary = args.outdir / "permutation_null_distribution.png"
    fig.savefig(out_png_primary, dpi=160)

    out_png_alias = args.outdir / "permutation_dist.png"
    fig.savefig(out_png_alias, dpi=160)

    plt.close(fig)

    print("Permutation test (difference in means)")
    print(f"Observed mean difference: {observed:.3f}")
    print(f"Two-sided p-value: {p_value:.6f}")
    print()
    print("Saved:", out_summary)
    print("Saved:", out_effect)
    print("Saved:", out_png_primary)
    print("Saved:", out_png_alias)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
