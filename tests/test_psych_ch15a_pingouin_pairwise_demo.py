import math

from scripts.psych_ch15_correlation import simulate_psych_correlation_dataset
from scripts.psych_ch15a_pingouin_pairwise_demo import compute_pairwise_corr


def _get_r(table, x: str, y: str) -> float:
    """Helper: extract r for the (x, y) pair in either order."""
    row = table.query("(X == @x and Y == @y) or (X == @y and Y == @x)").iloc[0]
    return float(row["r"])


def test_pairwise_corr_rowcount_matches_combinatorics():
    """pairwise_corr should return k*(k-1)/2 rows for k variables."""
    df = simulate_psych_correlation_dataset(n=120, random_state=456)
    k = len(df.columns)
    expected_pairs = k * (k - 1) // 2

    table = compute_pairwise_corr(
        method="pearson",
        padjust="none",
        n=120,
        random_state=456,
    )

    assert len(table) == expected_pairs


def test_stress_and_exam_score_are_strongly_negative():
    """Stress and exam score should have a reasonably strong negative r."""
    table = compute_pairwise_corr(
        method="pearson",
        padjust="none",
        n=300,
        random_state=999,
    )

    r = _get_r(table, "stress", "exam_score")

    assert r < -0.5
    assert r > -1.0
    assert not math.isnan(r)
