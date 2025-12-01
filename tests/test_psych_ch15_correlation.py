# tests/test_psych_ch15_correlation.py

import numpy as np

from scripts.psych_ch15_correlation import (
    pingouin_pearsonr,
    simulate_bivariate_correlation,
)


def test_simulate_bivariate_correlation_shape() -> None:
    df = simulate_bivariate_correlation(n=200, rho=0.3, random_state=42)
    assert df.shape == (200, 2)
    assert list(df.columns) == ["x", "y"]


def test_pingouin_matches_numpy_corr() -> None:
    df = simulate_bivariate_correlation(n=500, rho=0.4, random_state=123)
    r_np = np.corrcoef(df["x"], df["y"])[0, 1]
    r_pg = pingouin_pearsonr(df, "x", "y")
    assert abs(r_pg - r_np) < 1e-6


def test_pingouin_estimate_close_to_population_r() -> None:
    rho_true = 0.5
    df = simulate_bivariate_correlation(n=2000, rho=rho_true, random_state=999)
    r_pg = pingouin_pearsonr(df, "x", "y")
    # With n = 2000, the sample estimate should be very close to rho_true
    assert abs(r_pg - rho_true) < 0.05
