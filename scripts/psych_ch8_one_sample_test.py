# SPDX-License-Identifier: MIT
"""Chapter 8 helper: one-sample t-test via simulation on stress scores.

This script is part of the Track B (psychology) workflow in PyStatsV1.

It:

* generates a large synthetic population of ``stress_score`` values,
* draws one sample and computes the observed one-sample t-statistic,
* recenters the population to make H0 : mu = mu0 exactly true,
* simulates a null distribution of t-statistics by repeated sampling, and
* estimates a two-sided p-value by comparing |t_obs| to |t_sim|.

The goal is to connect the formal one-sample t-test to a simulation-based
view that students can see and experiment with.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


DATA_DIR = Path("data") / "synthetic"
OUT_DIR = Path("outputs") / "track_b"

DEFAULT_POP_SIZE = 50_000
DEFAULT_SAMPLE_SIZE = 25
DEFAULT_MU0 = 20.0
DEFAULT_N_SIM = 4_000
DEFAULT_SEED = 2025


@dataclass
class StressPopulation:
    """Container for the synthetic stress-score population."""

    scores: pd.Series

    @property
    def mean(self) -> float:
        return float(self.scores.mean())

    @property
    def sd(self) -> float:
        # Population SD (ddof=0) for reporting only
        return float(self.scores.std(ddof=0))


def generate_stress_population(
    n: int = DEFAULT_POP_SIZE,
    rng: np.random.Generator | None = None,
) -> StressPopulation:
    """Generate a synthetic 'stress_score' population.

    We use a simple normal-ish model with mean ~20 and SD ~10, then
    truncate at 0 to keep scores nonnegative.
    """
    if rng is None:
        rng = np.random.default_rng(DEFAULT_SEED)

    raw = rng.normal(loc=20.0, scale=10.0, size=n)
    scores = np.clip(raw, a_min=0.0, a_max=None)
    return StressPopulation(scores=pd.Series(scores, name="stress_score"))


def draw_sample(
    pop: StressPopulation,
    n: int,
    rng: np.random.Generator | None = None,
) -> np.ndarray:
    """Draw a simple random sample (without replacement) from the population."""
    if rng is None:
        rng = np.random.default_rng(DEFAULT_SEED)

    if n > len(pop.scores):
        msg = f"Sample size n={n} exceeds population size={len(pop.scores)}."
        raise ValueError(msg)

    idx = rng.choice(len(pop.scores), size=n, replace=False)
    return pop.scores.to_numpy()[idx]


def compute_t_stat(sample: np.ndarray, mu0: float) -> float:
    """Compute one-sample t-statistic for H0: mu = mu0.

    Uses sample mean and sample standard deviation (ddof=1).
    """
    xbar = float(sample.mean())
    s = float(sample.std(ddof=1))
    if s == 0.0:
        # Degenerate case; treat as no evidence against H0
        return 0.0
    se = s / np.sqrt(sample.size)
    return (xbar - mu0) / se


def recenter_population(pop: StressPopulation, mu0: float) -> StressPopulation:
    """Return a new population recentered so that mean == mu0.

    Shape and spread are preserved; only the center shifts.
    """
    current_mean = pop.mean
    shifted = pop.scores - current_mean + mu0
    return StressPopulation(scores=shifted)


def simulate_null_t_distribution(
    pop_under_h0: StressPopulation,
    n: int,
    mu0: float,
    n_sim: int = DEFAULT_N_SIM,
    rng: np.random.Generator | None = None,
) -> np.ndarray:
    """Simulate a null distribution of t-statistics under H0: mu = mu0."""
    if rng is None:
        rng = np.random.default_rng(DEFAULT_SEED + 1)

    t_vals = np.empty(n_sim, dtype=float)
    for i in range(n_sim):
        sample = draw_sample(pop_under_h0, n=n, rng=rng)
        t_vals[i] = compute_t_stat(sample, mu0=mu0)
    return t_vals


def estimate_two_sided_p(t_obs: float, t_null: np.ndarray) -> float:
    """Estimate two-sided p-value from a null distribution of t-statistics."""
    if t_null.size == 0:
        raise ValueError("Null distribution is empty.")
    extreme = np.abs(t_null) >= abs(t_obs)
    return float(extreme.mean())


def write_csv(path: Path, *, series: pd.Series | None = None, array: np.ndarray | None = None) -> Path:
    """Write either a Series or a 1D array to CSV with a simple column name."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if series is not None:
        series.to_csv(path, index=False)
    elif array is not None:
        pd.Series(array, name="t_null").to_csv(path, index=False)
    else:
        raise ValueError("Either 'series' or 'array' must be provided.")
    return path


def make_t_histogram(t_null: np.ndarray, t_obs: float, out_path: Path) -> Path:
    """Plot histogram of null t-statistics with observed t marked."""
    out_path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots()
    ax.hist(t_null, bins=40, density=True, alpha=0.7)
    ax.axvline(t_obs, color="black", linestyle="--", linewidth=1.5, label="observed t")
    ax.axvline(-t_obs, color="black", linestyle="--", linewidth=1.0, alpha=0.5)
    ax.set_xlabel("t under H0")
    ax.set_ylabel("Density")
    ax.set_title("Simulated null distribution of t-statistics")
    ax.legend(loc="best")

    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    return out_path


def main(
    pop_size: int = DEFAULT_POP_SIZE,
    sample_size: int = DEFAULT_SAMPLE_SIZE,
    mu0: float = DEFAULT_MU0,
    n_sim: int = DEFAULT_N_SIM,
    seed: int = DEFAULT_SEED,
    write_files: bool = True,
) -> int:
    """Run the Chapter 8 one-sample t-test simulation."""
    rng = np.random.default_rng(seed)

    # 1. Generate population
    pop = generate_stress_population(n=pop_size, rng=rng)
    print(f"Generated population with {pop_size} individuals")
    print(f"Population mean stress_score = {pop.mean:.2f}")
    print(f"Population SD   stress_score = {pop.sd:.2f}\n")

    # 2–3. Draw sample and compute observed t
    sample = draw_sample(pop, n=sample_size, rng=rng)
    xbar = float(sample.mean())
    s = float(sample.std(ddof=1))
    t_obs = compute_t_stat(sample, mu0=mu0)

    print(f"Null hypothesis: mu = {mu0:.2f}")
    print(f"Observed sample size n = {sample_size}")
    print(f"Observed sample mean   = {xbar:.2f}")
    print(f"Observed sample SD     = {s:.2f}")
    print(f"t statistic            = {t_obs:.2f}\n")

    # 4–5. Recenter population and simulate null t distribution
    pop_h0 = recenter_population(pop, mu0=mu0)
    t_null = simulate_null_t_distribution(
        pop_under_h0=pop_h0,
        n=sample_size,
        mu0=mu0,
        n_sim=n_sim,
        rng=rng,
    )

    # 6. Estimate p-value
    print(f"Using {n_sim} simulations under H0...")
    p_hat = estimate_two_sided_p(t_obs, t_null)
    print(f"Approximate two-sided p-value = {p_hat:.3f}")

    alpha = 0.05
    decision = "reject H0" if p_hat < alpha else "fail to reject H0"
    print(f"Decision at alpha = {alpha:.2f}: {decision}")

    # Optional outputs
    if write_files:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        OUT_DIR.mkdir(parents=True, exist_ok=True)

        write_csv(DATA_DIR / "psych_ch8_population_stress.csv", series=pop.scores)
        write_csv(DATA_DIR / "psych_ch8_null_t_values.csv", array=t_null)
        out_plot = OUT_DIR / "ch08_null_t_distribution.png"
        make_t_histogram(t_null, t_obs, out_plot)
        print()
        print(f"Wrote population to: {DATA_DIR / 'psych_ch8_population_stress.csv'}")
        print(f"Wrote null t-values to: {DATA_DIR / 'psych_ch8_null_t_values.csv'}")
        print(f"Wrote plot to: {out_plot}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
