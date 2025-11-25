import numpy as np
import pandas as pd
from scripts.psych_ch9_one_sample_ci import (
    draw_sample,
    one_sample_t_ci,
)


def test_draw_sample_deterministic():
    df = pd.DataFrame({"stress_score": np.arange(100)})
    sample1 = draw_sample(df, n=5, seed=1)
    sample2 = draw_sample(df, n=5, seed=1)
    assert np.array_equal(sample1, sample2)


def test_one_sample_t_ci_values():
    # deterministic sample
    sample = np.array([10, 20, 30, 40, 50], dtype=float)
    mu0 = 25.0

    res = one_sample_t_ci(sample, mu0=mu0)
    # hand-computed or numpy-verified values
    assert res["n"] == 5
    assert res["df"] == 4

    # mean, sd, se
    assert abs(res["xbar"] - 30.0) < 1e-6
    assert abs(res["s"] - np.std(sample, ddof=1)) < 1e-6
    assert abs(res["se"] - res["s"] / np.sqrt(5)) < 1e-6

    # t-stat
    expected_t = (30.0 - 25.0) / (res["s"] / np.sqrt(5))
    assert abs(res["t_stat"] - expected_t) < 1e-6

    # CI covers mean
    assert res["ci_low"] < res["xbar"] < res["ci_high"]