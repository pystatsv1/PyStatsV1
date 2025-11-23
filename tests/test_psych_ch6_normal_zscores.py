from pathlib import Path

import pandas as pd

from scripts.psych_ch6_normal_zscores import compute_zscores, summarize_tails


def test_compute_zscores_basic_properties():
    series = pd.Series([1.0, 2.0, 3.0, 4.0])
    z = compute_zscores(series)

    # z-scores should have mean ~ 0 and sd ~ 1
    assert abs(z.mean()) < 1e-12
    assert abs(z.std(ddof=1) - 1.0) < 1e-12


def test_summarize_tails_counts_correct():
    # Symmetric around zero: 4 small, 2 medium, 2 large
    z = pd.Series([-3, -2.1, -1, -0.5, 0.5, 1, 2.1, 3])

    tails = summarize_tails(z)
    # 4 of 8 have |z| > 2.0 -> 0.5
    # 2 of 8 have |z| > 3.0? No, strictly > 3 is 0; if you want >= change condition.
    assert tails["prop_gt_2"] == 0.5
    assert tails["prop_gt_3"] == 0.0