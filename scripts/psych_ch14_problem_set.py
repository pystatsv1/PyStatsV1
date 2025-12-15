"""
Track C — Chapter 14 Problem Set (Repeated-Measures ANOVA).

This module generates small, deterministic datasets for three exercises and
runs a one-factor repeated-measures ANOVA (within-subjects factor: time).

We use statsmodels' AnovaRM for the omnibus test, and compute partial eta^2
(np2) from F and dfs:

    np2 = (F * df1) / (F * df1 + df2)

Optionally (if pingouin is installed), we also compute Mauchly's test of
sphericity and Greenhouse–Geisser epsilon + a GG-corrected p-value.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.anova import AnovaRM


@dataclass(frozen=True)
class ProblemResult:
    """Container for a single problem-set exercise result."""

    name: str
    data: pd.DataFrame
    anova_table: pd.DataFrame


def _ar1_cov(n: int, sd: float, rho: float) -> np.ndarray:
    idx = np.arange(n)
    return (sd**2) * (rho ** np.abs(np.subtract.outer(idx, idx)))


def simulate_repeated_measures_data(
    n_subjects: int,
    time_labels: Sequence[str],
    means: Sequence[float],
    sd: float,
    random_state: int,
    *,
    cov: np.ndarray | None = None,
) -> pd.DataFrame:
    """
    Simulate long-format repeated-measures data.

    Output columns: {"subject", "time", "score"}.

    If cov is provided, it is used as the covariance matrix of the within-subject
    errors (multivariate normal), allowing us to simulate sphericity violations.
    """
    if len(time_labels) != len(means):
        raise ValueError("time_labels and means must have the same length")

    rng = np.random.default_rng(random_state)
    n_times = len(time_labels)

    rows: list[tuple[int, str, float]] = []
    if cov is None:
        for s in range(1, n_subjects + 1):
            for t, m in zip(time_labels, means):
                score = float(rng.normal(loc=m, scale=sd))
                rows.append((s, t, score))
    else:
        cov = np.asarray(cov, dtype=float)
        if cov.shape != (n_times, n_times):
            raise ValueError("cov must be shape (n_times, n_times)")
        for s in range(1, n_subjects + 1):
            errors = rng.multivariate_normal(mean=np.zeros(n_times), cov=cov)
            for t, m, e in zip(time_labels, means, errors):
                rows.append((s, t, float(m + e)))

    df = pd.DataFrame(rows, columns=["subject", "time", "score"])
    df["subject"] = df["subject"].astype(int)
    df["time"] = df["time"].astype(str)
    return df


def run_repeated_measures_anova(data: pd.DataFrame) -> pd.DataFrame:
    """
    Run one-way repeated-measures ANOVA (within factor: time).

    Returns a 1-row DataFrame with columns:
      - F, df1, df2, p-unc, np2
    And (optionally, if pingouin is available):
      - W-spher, p-spher, eps-GG, p-GG-corr
    """
    required = {"subject", "time", "score"}
    missing = required - set(data.columns)
    if missing:
        raise ValueError(f"Data missing required columns: {sorted(missing)}")

    # statsmodels repeated-measures ANOVA
    aov = AnovaRM(data, depvar="score", subject="subject", within=["time"]).fit()
    table = aov.anova_table.copy()

    # statsmodels table has 1 row for the within factor, indexed by "time"
    row = table.iloc[0]
    F = float(row["F Value"])
    df1 = float(row["Num DF"])
    df2 = float(row["Den DF"])
    p_unc = float(row["Pr > F"])

    # partial eta^2 from F and dfs
    np2 = (F * df1) / (F * df1 + df2) if (F * df1 + df2) > 0 else float("nan")

    out = pd.DataFrame(
        [
            {
                "effect": "time",
                "F": F,
                "df1": df1,
                "df2": df2,
                "p-unc": p_unc,
                "np2": np2,
            }
        ]
    )

    # Optional: sphericity + GG correction via pingouin if present
    try:
        import pingouin as pg  # type: ignore

        # Mauchly's test of sphericity
        W, chi2, dof, p_spher = pg.sphericity(
            data=data, dv="score", subject="subject", within="time"
        )
        eps_gg = float(pg.epsilon(data=data, dv="score", subject="subject", within="time"))

        # GG-corrected dfs and p-value
        df1_gg = max(eps_gg * df1, 1e-9)
        df2_gg = max(eps_gg * df2, 1e-9)
        p_gg = float(stats.f.sf(F, df1_gg, df2_gg))

        out["W-spher"] = float(W)
        out["p-spher"] = float(p_spher)
        out["eps-GG"] = float(eps_gg)
        out["p-GG-corr"] = float(p_gg)

    except Exception:
        # Keep the core output stable even if pingouin isn't available
        pass

    return out


# ----------------------------
# Exercises (Track C style)
# ----------------------------

def exercise_1_clear_time_effect(*, random_state: int = 123) -> ProblemResult:
    """
    Exercise 1: Clear improvement over time (should be significant).
    3 time points, strong mean differences.
    """
    time_labels = ["T1", "T2", "T3"]
    means = [50.0, 58.0, 66.0]
    data = simulate_repeated_measures_data(
        n_subjects=30, time_labels=time_labels, means=means, sd=6.0, random_state=random_state
    )
    anova_table = run_repeated_measures_anova(data)
    return ProblemResult(name="Exercise 1 — clear time effect", data=data, anova_table=anova_table)


def exercise_2_no_time_effect(*, random_state: int = 456) -> ProblemResult:
    """
    Exercise 2: No true time effect (should be non-significant; tiny np2).
    4 time points, equal means.
    """
    time_labels = ["T1", "T2", "T3", "T4"]
    means = [0.0, 0.0, 0.0, 0.0]
    data = simulate_repeated_measures_data(
        n_subjects=40, time_labels=time_labels, means=means, sd=5.0, random_state=random_state
    )
    anova_table = run_repeated_measures_anova(data)
    return ProblemResult(name="Exercise 2 — no time effect", data=data, anova_table=anova_table)


def exercise_3_correlated_errors_sphericity_risk(*, random_state: int = 789) -> ProblemResult:
    """
    Exercise 3: Moderate time effect with correlated within-subject errors.
    This is a realistic setup where sphericity *may* be questionable.
    """
    time_labels = ["T1", "T2", "T3", "T4"]
    means = [10.0, 12.0, 14.0, 16.0]
    cov = _ar1_cov(n=len(time_labels), sd=5.0, rho=0.85)

    data = simulate_repeated_measures_data(
        n_subjects=35,
        time_labels=time_labels,
        means=means,
        sd=5.0,
        random_state=random_state,
        cov=cov,
    )
    anova_table = run_repeated_measures_anova(data)
    return ProblemResult(
        name="Exercise 3 — correlated errors (sphericity risk)",
        data=data,
        anova_table=anova_table,
    )


def _print_result(result: ProblemResult) -> None:
    print()
    print("=" * 80)
    print(result.name)
    print("-" * 80)
    print("Data head:")
    print(result.data.head(10).to_string(index=False))
    print()
    print("Repeated-measures ANOVA:")
    print(result.anova_table.to_string(index=False))
    print("=" * 80)


def main(argv: Iterable[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="Track C — Chapter 14 problem set (Repeated-Measures ANOVA)."
    )
    parser.add_argument(
        "--exercise",
        choices=["1", "2", "3", "all"],
        default="all",
        help="Which exercise to run (default: all).",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.exercise in ("1", "all"):
        _print_result(exercise_1_clear_time_effect())
    if args.exercise in ("2", "all"):
        _print_result(exercise_2_no_time_effect())
    if args.exercise in ("3", "all"):
        _print_result(exercise_3_correlated_errors_sphericity_risk())

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
