"""Track C — Chapter 16 problem set (Linear Regression).

Goal: Provide deterministic, runnable exercises for:
- Simple linear regression (y = a + b x)
- Standard error of the estimate (SEE)
- Multiple regression and incremental R^2

Each exercise returns a ProblemResult containing:
- the generated dataset (pandas DataFrame)
- a tidy regression coefficient table
- R^2 (and SEE for simple regression)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

import numpy as np
import pandas as pd
from scipy import stats


@dataclass(frozen=True)
class ProblemResult:
    """Standard container returned by each Track C problem-set exercise."""

    data: pd.DataFrame
    model_table: pd.DataFrame
    r2: float
    see: float | None = None
    y_col: str = "y"
    x_cols: list[str] = field(default_factory=list)
    extra_tables: dict[str, pd.DataFrame] = field(default_factory=dict)
    extra_metrics: dict[str, float] = field(default_factory=dict)


def _ols_fit(X: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, float, float]:
    """Fit OLS with intercept already included in X.

    Returns:
        beta, se, tvals, pvals, r2, sigma (sqrt(MSE))
    """
    n, p = X.shape
    if n <= p:
        raise ValueError("Need more rows than parameters for OLS.")

    # Use pseudo-inverse for stability (handles mild collinearity better than inv)
    xtx_inv = np.linalg.pinv(X.T @ X)
    beta = xtx_inv @ (X.T @ y)

    y_hat = X @ beta
    resid = y - y_hat

    sse = float(np.sum(resid**2))
    sst = float(np.sum((y - float(np.mean(y))) ** 2))
    r2 = 1.0 - (sse / sst) if sst > 0 else 0.0

    df = n - p
    mse = sse / df
    sigma = float(np.sqrt(mse))

    var_beta = mse * xtx_inv
    se = np.sqrt(np.diag(var_beta))

    # Avoid division by zero in pathological cases
    tvals = np.divide(beta, se, out=np.zeros_like(beta), where=se > 0)
    pvals = 2.0 * stats.t.sf(np.abs(tvals), df=df)

    return beta, se, tvals, pvals, r2, sigma


def run_linear_regression(
    data: pd.DataFrame, *, y: str, x_cols: Iterable[str]
) -> tuple[pd.DataFrame, float, float]:
    """Run OLS linear regression (simple or multiple) and return a tidy table + metrics."""
    x_cols_list = list(x_cols)
    if not x_cols_list:
        raise ValueError("x_cols must contain at least one predictor column.")

    y_vec = data[y].to_numpy(dtype=float)
    X = np.column_stack([np.ones(len(data), dtype=float)] + [data[c].to_numpy(dtype=float) for c in x_cols_list])

    beta, se, tvals, pvals, r2, sigma = _ols_fit(X, y_vec)

    terms = ["Intercept", *x_cols_list]
    table = pd.DataFrame(
        {
            "term": terms,
            "coef": beta,
            "se": se,
            "t": tvals,
            "p": pvals,
        }
    )
    return table, float(r2), float(sigma)


# -------------------------
# Exercise generators
# -------------------------

def exercise_1_strong_simple_regression(*, random_state: int = 123, n: int = 200) -> ProblemResult:
    """Exercise 1: Strong simple regression with good predictive signal.

    Typical expectation:
    - slope significantly non-zero
    - R^2 moderately high (roughly ~0.45–0.60 depending on seed)
    """
    rng = np.random.default_rng(random_state)
    x = rng.normal(loc=0.0, scale=1.0, size=n)
    # y = 10 + 2x + noise, noise ~ N(0, 2)
    y = 10.0 + 2.0 * x + rng.normal(loc=0.0, scale=2.0, size=n)

    df = pd.DataFrame({"x": x, "y": y})
    table, r2, see = run_linear_regression(df, y="y", x_cols=["x"])

    return ProblemResult(data=df, model_table=table, r2=r2, see=see, y_col="y", x_cols=["x"])


def exercise_2_weak_noisy_regression(*, random_state: int = 456, n: int = 200) -> ProblemResult:
    """Exercise 2: Weak regression — small slope drowned by noise.

    Typical expectation:
    - R^2 small (near zero)
    - slope may be significant or not depending on seed, but effect is small
    """
    rng = np.random.default_rng(random_state)
    x = rng.normal(loc=0.0, scale=1.0, size=n)
    # y = 5 + 0.5x + noise, noise ~ N(0, 4) -> low R^2
    y = 5.0 + 0.5 * x + rng.normal(loc=0.0, scale=4.0, size=n)

    df = pd.DataFrame({"x": x, "y": y})
    table, r2, see = run_linear_regression(df, y="y", x_cols=["x"])

    return ProblemResult(data=df, model_table=table, r2=r2, see=see, y_col="y", x_cols=["x"])


def exercise_3_multiple_regression_incremental_r2(*, random_state: int = 789, n: int = 240) -> ProblemResult:
    """Exercise 3: Multiple regression with incremental R^2.

    Construct:
    - x1 is a strong predictor
    - x2 shares variance with x1, but has its own unique contribution
    Expectation:
    - R^2 (x1 + x2) > R^2 (x1 only) by a meaningful margin
    - x2 coefficient usually significant
    """
    rng = np.random.default_rng(random_state)

    x1 = rng.normal(0.0, 1.0, size=n)
    # correlated predictor: x2 = 0.6*x1 + noise
    x2 = 0.6 * x1 + rng.normal(0.0, 0.8, size=n)

    # y depends on BOTH (unique contribution) + noise
    y = 3.0 + 1.6 * x1 + 1.0 * x2 + rng.normal(0.0, 2.0, size=n)

    df = pd.DataFrame({"x1": x1, "x2": x2, "y": y})

    simple_table, r2_simple, _ = run_linear_regression(df, y="y", x_cols=["x1"])
    multiple_table, r2_multiple, _ = run_linear_regression(df, y="y", x_cols=["x1", "x2"])

    return ProblemResult(
        data=df,
        model_table=multiple_table,
        r2=r2_multiple,
        see=None,
        y_col="y",
        x_cols=["x1", "x2"],
        extra_tables={"simple": simple_table, "multiple": multiple_table},
        extra_metrics={"r2_simple": r2_simple, "r2_multiple": r2_multiple, "delta_r2": (r2_multiple - r2_simple)},
    )


def _print_result(title: str, result: ProblemResult) -> None:
    print(f"\n=== {title} ===")
    print(f"Columns: y={result.y_col}, x={result.x_cols}")
    print(f"R^2 = {result.r2:.4f}")
    if result.see is not None:
        print(f"SEE = {result.see:.4f}")
    print("\nModel table:")
    print(result.model_table.to_string(index=False))

    if result.extra_tables:
        print("\nExtra tables:")
        for name, tbl in result.extra_tables.items():
            print(f"\n-- {name} --")
            print(tbl.to_string(index=False))

    if result.extra_metrics:
        print("\nExtra metrics:")
        for k, v in result.extra_metrics.items():
            print(f"{k}: {v:.4f}")


def main() -> None:
    """Run all Track C Chapter 16 exercises."""
    r1 = exercise_1_strong_simple_regression()
    r2 = exercise_2_weak_noisy_regression()
    r3 = exercise_3_multiple_regression_incremental_r2()

    _print_result("Exercise 1 — Strong simple regression", r1)
    _print_result("Exercise 2 — Weak/noisy regression", r2)
    _print_result("Exercise 3 — Multiple regression & incremental R^2", r3)


if __name__ == "__main__":
    main()
