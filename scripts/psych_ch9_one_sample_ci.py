"""
Chapter 9: One-Sample t-Test and Confidence Interval (Track B)

This script loads a synthetic population of "stress_score" values,
draws a simple random sample, computes the analytic one-sample t-test,
and prints a 95% confidence interval.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pathlib import Path
from scipy.stats import t

DATA_DIR = Path("data/synthetic")
OUTPUT_DIR = Path("outputs/track_b")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

POP_PATH = DATA_DIR / "psych_ch7_population_stress.csv"


def load_population(path: Path = POP_PATH) -> pd.DataFrame:
    """Load the large synthetic stress-score population generated earlier."""
    return pd.read_csv(path)


def draw_sample(df: pd.DataFrame, n: int, seed: int = 0) -> pd.Series:
    """Draw a simple random sample of size n."""
    rng = np.random.default_rng(seed)
    return rng.choice(df["stress_score"].values, size=n, replace=False)


def one_sample_t_ci(sample: np.ndarray, mu0: float, alpha: float = 0.05) -> dict:
    """
    Compute analytic one-sample t-test and 95% confidence interval.
    Returns a dictionary with xbar, s, se, t_stat, df, p_value, ci_low, ci_high.
    """
    n = len(sample)
    df = n - 1

    xbar = float(np.mean(sample))
    s = float(np.std(sample, ddof=1))
    se = s / np.sqrt(n)

    t_stat = (xbar - mu0) / se

    # two-sided p-value
    p_value = 2 * (1 - t.cdf(abs(t_stat), df=df))

    # 95% confidence interval
    tcrit = t.ppf(1 - alpha / 2, df)
    ci_low = xbar - tcrit * se
    ci_high = xbar + tcrit * se

    return {
        "n": n,
        "df": df,
        "xbar": xbar,
        "s": s,
        "se": se,
        "t_stat": t_stat,
        "p_value": p_value,
        "ci_low": ci_low,
        "ci_high": ci_high,
    }


def main():
    pop = load_population()
    print(f"Loaded synthetic population with {len(pop)} individuals")
    print(f"Population mean stress_score = {pop.stress_score.mean():.2f}")
    print(f"Population SD   stress_score = {pop.stress_score.std(ddof=1):.2f}\n")

    n = 25
    mu0 = 20.0

    sample = draw_sample(pop, n=n, seed=42)
    results = one_sample_t_ci(sample, mu0=mu0)

    print(f"Drawn sample size n = {results['n']}")
    print(f"Sample mean = {results['xbar']:.2f}")
    print(f"Sample SD   = {results['s']:.2f}")
    print(f"SE          = {results['se']:.2f}")
    print(f"t statistic = {results['t_stat']:.2f}")
    print(f"df          = {results['df']}\n")

    print(f"Analytic two-sided p-value = {results['p_value']:.3f}")
    print(f"95% CI = [{results['ci_low']:.2f}, {results['ci_high']:.2f}]")


if __name__ == "__main__":
    main()
