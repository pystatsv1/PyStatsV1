"""
Track C — Chapter 15 Problem Set (Correlation).

Exercises:
1) Strong Pearson correlation (clear relationship).
2) Near-zero correlation (no relationship).
3) Third-variable problem: strong raw correlation, but near-zero partial correlation
   after controlling for Z.

We compute:
- Pearson r and p-value (scipy.stats.pearsonr)
- Fisher-z CI for r
- Partial correlation via residualization (OLS with intercept using lstsq)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

import numpy as np
import pandas as pd
from scipy import stats


@dataclass(frozen=True)
class CorrResult:
    x: str
    y: str
    n: int
    r: float
    p: float
    ci95_lo: float
    ci95_hi: float


@dataclass(frozen=True)
class PartialCorrResult:
    x: str
    y: str
    controls: tuple[str, ...]
    n: int
    r_partial: float
    p: float


@dataclass(frozen=True)
class ProblemResult:
    name: str
    data: pd.DataFrame
    pearson: CorrResult | None
    partial: PartialCorrResult | None
    corr_matrix: pd.DataFrame | None


def _fisher_ci(r: float, n: int, alpha: float = 0.05) -> tuple[float, float]:
    """95% CI for Pearson r via Fisher z transform."""
    if n < 4:
        return (float("nan"), float("nan"))
    r = float(np.clip(r, -0.999999, 0.999999))
    z = np.arctanh(r)
    se = 1.0 / np.sqrt(n - 3)
    zcrit = stats.norm.ppf(1 - alpha / 2)
    lo = np.tanh(z - zcrit * se)
    hi = np.tanh(z + zcrit * se)
    return (float(lo), float(hi))


def pearson_corr(df: pd.DataFrame, x: str, y: str) -> CorrResult:
    xs = df[x].to_numpy(dtype=float)
    ys = df[y].to_numpy(dtype=float)
    r, p = stats.pearsonr(xs, ys)
    lo, hi = _fisher_ci(r, n=len(df))
    return CorrResult(x=x, y=y, n=len(df), r=float(r), p=float(p), ci95_lo=lo, ci95_hi=hi)


def _residualize(y: np.ndarray, X: np.ndarray) -> np.ndarray:
    """
    Residualize y on X with an intercept using least squares.
    X should be shape (n, k). Returns residuals shape (n,).
    """
    n = y.shape[0]
    X_design = np.column_stack([np.ones(n), X])
    beta, *_ = np.linalg.lstsq(X_design, y, rcond=None)
    y_hat = X_design @ beta
    return y - y_hat


def partial_corr(df: pd.DataFrame, x: str, y: str, controls: Sequence[str]) -> PartialCorrResult:
    """
    Partial correlation r_{xy·Z} via residualization:
      r = corr(resid(x|Z), resid(y|Z))
    """
    if len(controls) == 0:
        raise ValueError("controls must be non-empty for partial correlation")

    X = df[x].to_numpy(dtype=float)
    Y = df[y].to_numpy(dtype=float)
    Z = df[list(controls)].to_numpy(dtype=float)

    rx = _residualize(X, Z)
    ry = _residualize(Y, Z)

    r, p = stats.pearsonr(rx, ry)
    return PartialCorrResult(x=x, y=y, controls=tuple(controls), n=len(df), r_partial=float(r), p=float(p))


def corr_matrix(df: pd.DataFrame, cols: Sequence[str]) -> pd.DataFrame:
    mat = df[list(cols)].corr(method="pearson")
    return mat


# ----------------------------
# Exercises
# ----------------------------

def exercise_1_strong_positive(*, random_state: int = 123) -> ProblemResult:
    """
    Exercise 1: Strong positive correlation.
    Expect: r large (> 0.7) and p < 0.001.
    """
    rng = np.random.default_rng(random_state)
    n = 80
    x = rng.normal(0, 1, size=n)
    y = 0.85 * x + rng.normal(0, 0.55, size=n)

    df = pd.DataFrame({"x": x, "y": y})
    pr = pearson_corr(df, "x", "y")

    return ProblemResult(
        name="Exercise 1 — strong positive correlation",
        data=df,
        pearson=pr,
        partial=None,
        corr_matrix=corr_matrix(df, ["x", "y"]),
    )


def exercise_2_near_zero(*, random_state: int = 456) -> ProblemResult:
    """
    Exercise 2: Near-zero correlation.
    Expect: |r| small (< 0.15) and typically non-significant.
    """
    rng = np.random.default_rng(random_state)
    n = 120
    x = rng.normal(0, 1, size=n)
    y = rng.normal(0, 1, size=n)

    df = pd.DataFrame({"x": x, "y": y})
    pr = pearson_corr(df, "x", "y")

    return ProblemResult(
        name="Exercise 2 — near-zero correlation",
        data=df,
        pearson=pr,
        partial=None,
        corr_matrix=corr_matrix(df, ["x", "y"]),
    )


def exercise_3_third_variable_partial(*, random_state: int = 789) -> ProblemResult:
    """
    Exercise 3: Third-variable problem.
    Build X and Y so they share Z, creating a strong raw correlation.
    After controlling for Z, the partial correlation should be near zero.
    """
    rng = np.random.default_rng(random_state)
    n = 200

    z = rng.normal(0, 1, size=n)
    x = 1.25 * z + rng.normal(0, 1.0, size=n)
    y = 1.25 * z + rng.normal(0, 1.0, size=n)

    df = pd.DataFrame({"x": x, "y": y, "z": z})
    pr = pearson_corr(df, "x", "y")
    pc = partial_corr(df, "x", "y", controls=["z"])

    return ProblemResult(
        name="Exercise 3 — third-variable problem (partial correlation)",
        data=df,
        pearson=pr,
        partial=pc,
        corr_matrix=corr_matrix(df, ["x", "y", "z"]),
    )


def _print_result(res: ProblemResult) -> None:
    print()
    print("=" * 80)
    print(res.name)
    print("-" * 80)
    print("Data head:")
    print(res.data.head(10).to_string(index=False))

    if res.pearson is not None:
        p = res.pearson
        print()
        print("Pearson correlation:")
        print(f"  r({p.n - 2}) = {p.r:.3f}, p = {p.p:.4g}, 95% CI [{p.ci95_lo:.3f}, {p.ci95_hi:.3f}]")

    if res.partial is not None:
        pc = res.partial
        print()
        print("Partial correlation:")
        print(f"  r_partial({pc.n - 2 - len(pc.controls)}) = {pc.r_partial:.3f}, p = {pc.p:.4g}  (controls={pc.controls})")

    if res.corr_matrix is not None:
        print()
        print("Correlation matrix:")
        print(res.corr_matrix.to_string())

    print("=" * 80)


def main(argv: Iterable[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="Track C — Chapter 15 problem set (Correlation)."
    )
    parser.add_argument(
        "--exercise",
        choices=["1", "2", "3", "all"],
        default="all",
        help="Which exercise to run (default: all).",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.exercise in ("1", "all"):
        _print_result(exercise_1_strong_positive())
    if args.exercise in ("2", "all"):
        _print_result(exercise_2_near_zero())
    if args.exercise in ("3", "all"):
        _print_result(exercise_3_third_variable_partial())

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
