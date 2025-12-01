import math

import pingouin as pg

from scripts.psych_ch15_correlation import simulate_psych_correlation_dataset
from scripts.psych_ch15a_pingouin_partial_demo import compute_partial_corr


def test_partial_smaller_than_zero_order_for_study_vs_exam():
    """Controlling for stress should shrink study_hours–exam_score r."""
    df = simulate_psych_correlation_dataset(n=400, random_state=123)

    zero = pg.corr(df["study_hours"], df["exam_score"])
    r_zero = float(zero["r"].iloc[0])

    r_partial = compute_partial_corr(
        df,
        x="study_hours",
        y="exam_score",
        covars=["stress"],
    )

    assert 0.0 < r_partial < r_zero
    assert not math.isnan(r_partial)


def test_two_covariates_do_not_increase_magnitude():
    """Adding anxiety as a covariate should not make r much larger."""
    df = simulate_psych_correlation_dataset(n=400, random_state=321)

    r_partial_stress = compute_partial_corr(
        df,
        x="study_hours",
        y="exam_score",
        covars=["stress"],
    )

    r_partial_two = compute_partial_corr(
        df,
        x="study_hours",
        y="exam_score",
        covars=["stress", "anxiety"],
    )

    # In this synthetic design, controlling for an extra covariate should
    # shrink or at least not greatly increase the magnitude of r.
    assert abs(r_partial_two) <= abs(r_partial_stress) + 0.05
