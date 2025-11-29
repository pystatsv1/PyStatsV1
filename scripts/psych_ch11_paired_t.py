"""Chapter 11: Paired (Dependent) Samples t-Test utilities for Track B.

This module provides:

* A deterministic simulator for a pre–post training study:
    - simulate_paired_training_study

* A paired-samples t-test built from raw scores:
    - paired_t_test_from_wide

* A mis-specified independent-samples t-test for teaching purposes:
    - mis_specified_independent_t

The goal is to keep the code simple, explicit, and fully reproducible so that
students can trace every step in the analysis.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Optional, Union

import numpy as np
import pandas as pd
from scipy import stats

Number = Union[int, float]
RandomStateLike = Union[int, np.random.Generator, None]


@dataclass
class PairedTResult:
    """Container for paired-samples t-test results."""

    n: int
    mean_pre: float
    mean_post: float
    mean_diff: float
    sd_diff: float
    se_diff: float
    df: int
    t_stat: float
    p_value_two_sided: float
    ci_low: float
    ci_high: float
    dz: float  # Cohen's d_z effect size


def _get_rng(random_state: RandomStateLike) -> np.random.Generator:
    """Return a NumPy Generator from an int seed or an existing Generator."""
    if isinstance(random_state, np.random.Generator):
        return random_state
    return np.random.default_rng(random_state)


def simulate_paired_training_study(
    n: int = 30,
    mean_pre: Number = 72.0,
    mean_change: Number = 5.0,
    sd_pre: Number = 10.0,
    sd_change: Number = 8.0,
    random_state: RandomStateLike = 11,
) -> pd.DataFrame:
    """Simulate a simple pre–post training study with paired scores.

    Parameters
    ----------
    n
        Number of participants (pairs of observations).
    mean_pre
        Population mean for the pre-training scores.
    mean_change
        Population mean change from pre to post (post - pre).
    sd_pre
        Population standard deviation for pre-training scores.
    sd_change
        Population standard deviation for change scores.
    random_state
        Integer seed, NumPy Generator, or None for randomness. Passing an
        explicit seed or Generator makes the simulation fully reproducible.

    Returns
    -------
    pandas.DataFrame
        A DataFrame with columns:
        - participant_id
        - score_pre
        - score_post
        - diff (post - pre)
    """
    rng = _get_rng(random_state)

    pre = rng.normal(loc=mean_pre, scale=sd_pre, size=n)
    change = rng.normal(loc=mean_change, scale=sd_change, size=n)
    post = pre + change
    diff = post - pre

    return pd.DataFrame(
        {
            "participant_id": np.arange(1, n + 1),
            "score_pre": pre,
            "score_post": post,
            "diff": diff,
        }
    )


def paired_t_test_from_wide(
    df: pd.DataFrame,
    *,
    pre_col: str = "score_pre",
    post_col: str = "score_post",
    alpha: float = 0.05,
) -> PairedTResult:
    """Compute a paired-samples t-test from a wide-format DataFrame.

    Parameters
    ----------
    df
        DataFrame containing (at least) pre and post columns for each participant.
    pre_col
        Column name for pre-training scores.
    post_col
        Column name for post-training scores.
    alpha
        Two-sided alpha level for the confidence interval.

    Returns
    -------
    PairedTResult
        Dataclass with sample summaries, t-statistic, p-value, CI, and d_z.
    """
    pre = df[pre_col].to_numpy()
    post = df[post_col].to_numpy()

    diff = post - pre
    n = diff.size

    mean_pre = float(np.mean(pre))
    mean_post = float(np.mean(post))
    mean_diff = float(np.mean(diff))
    sd_diff = float(np.std(diff, ddof=1))
    se_diff = float(sd_diff / np.sqrt(n))

    dfree = n - 1
    t_stat = float(mean_diff / se_diff)

    p_value = float(2.0 * stats.t.sf(abs(t_stat), df=dfree))
    t_crit = float(stats.t.ppf(1.0 - alpha / 2.0, df=dfree))

    ci_low = float(mean_diff - t_crit * se_diff)
    ci_high = float(mean_diff + t_crit * se_diff)

    # Cohen's d_z: mean difference in SD units of the difference scores.
    dz = float(mean_diff / sd_diff) if sd_diff > 0.0 else 0.0

    return PairedTResult(
        n=n,
        mean_pre=mean_pre,
        mean_post=mean_post,
        mean_diff=mean_diff,
        sd_diff=sd_diff,
        se_diff=se_diff,
        df=dfree,
        t_stat=t_stat,
        p_value_two_sided=p_value,
        ci_low=ci_low,
        ci_high=ci_high,
        dz=dz,
    )


def mis_specified_independent_t(
    df: pd.DataFrame,
    *,
    pre_col: str = "score_pre",
    post_col: str = "score_post",
) -> dict[str, float]:
    """Compute a mis-specified independent-samples t-test for teaching.

    This function deliberately ignores the pairing and treats pre and post
    scores as if they came from two independent groups. It is provided purely
    to illustrate the loss of power that occurs when we use the wrong model
    for the design.

    Parameters
    ----------
    df
        DataFrame containing pre and post columns.
    pre_col
        Column name for pre-training scores.
    post_col
        Column name for post-training scores.

    Returns
    -------
    dict
        Dictionary with n1, n2, means, variances, pooled variance, t-statistic,
        degrees of freedom, and two-sided p-value.
    """
    pre = df[pre_col].to_numpy()
    post = df[post_col].to_numpy()

    n1 = pre.size
    n2 = post.size

    mean1 = float(np.mean(pre))
    mean2 = float(np.mean(post))
    var1 = float(np.var(pre, ddof=1))
    var2 = float(np.var(post, ddof=1))

    dfree = n1 + n2 - 2
    sp2 = ((n1 - 1) * var1 + (n2 - 1) * var2) / dfree
    se = float(np.sqrt(sp2 * (1.0 / n1 + 1.0 / n2)))
    t_stat = float((mean2 - mean1) / se)
    p_value = float(2.0 * stats.t.sf(abs(t_stat), df=dfree))

    return {
        "n1": n1,
        "n2": n2,
        "mean1": mean1,
        "mean2": mean2,
        "var1": var1,
        "var2": var2,
        "sp2": float(sp2),
        "se": se,
        "df": dfree,
        "t_stat": t_stat,
        "p_value_two_sided": p_value,
    }


def _build_arg_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser for Chapter 11."""
    parser = argparse.ArgumentParser(
        description=(
            "Simulate and analyze a pre–post training study "
            "using a paired-samples t-test."
        )
    )
    parser.add_argument(
        "--n",
        type=int,
        default=40,
        help="Number of participants (default: 40).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=2025,
        help="Random seed for the simulator (default: 2025).",
    )
    parser.add_argument(
        "--alpha",
        type=float,
        default=0.05,
        help="Two-sided alpha level for the CI (default: 0.05).",
    )
    parser.add_argument(
        "--csv",
        type=str,
        default=None,
        help=(
            "Optional path to write the simulated dataset as CSV. "
            "Parent directories are created if necessary."
        ),
    )
    return parser


def main(argv: Optional[list[str]] = None) -> None:
    """Command-line entry point for Chapter 11."""
    parser = _build_arg_parser()
    args = parser.parse_args(argv)

    df = simulate_paired_training_study(n=args.n, random_state=args.seed)

    if args.csv:
        import pathlib

        path = pathlib.Path(args.csv)
        path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(path, index=False)

    result = paired_t_test_from_wide(df, alpha=args.alpha)

    print("Paired samples t-test for pre–post training study")
    print(f"n = {result.n}, df = {result.df}")
    print(f"Mean(pre)  = {result.mean_pre:.2f}")
    print(f"Mean(post) = {result.mean_post:.2f}")
    print(f"Mean diff  = {result.mean_diff:.2f}")
    print(
        f"t({result.df}) = {result.t_stat:.3f}, "
        f"p = {result.p_value_two_sided:.4f}"
    )
    print(
        f"{int((1.0 - args.alpha) * 100)}% CI for mean diff: "
        f"[{result.ci_low:.2f}, {result.ci_high:.2f}]"
    )
    print(f"Cohen's d_z = {result.dz:.2f}")


if __name__ == "__main__":
    main()
