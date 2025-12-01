import pandas as pd
import pytest

from scripts.psych_ch14a_pingouin_mixed_demo import (
    simulate_mixed_design_data,
    run_pingouin_mixed_anova,
)


def test_simulate_mixed_design_data_structure():
    """Mixed design demo should return long-format data with group, time, and stress_score."""
    df = simulate_mixed_design_data()

    assert isinstance(df, pd.DataFrame)
    for col in ["subject", "group", "time", "stress_score"]:
        assert col in df.columns

    # At least two groups and two time points
    assert df["group"].nunique() >= 2
    assert df["time"].nunique() >= 2

    # Each subject should have multiple rows (within-subject time factor)
    counts_per_subject = df["subject"].value_counts()
    assert counts_per_subject.min() >= 2


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_run_pingouin_mixed_anova_returns_table():
    """Pingouin mixed_anova wrapper should return a non-empty ANOVA table."""
    df = simulate_mixed_design_data()
    anova_table = run_pingouin_mixed_anova(df)

    assert isinstance(anova_table, pd.DataFrame)
    assert not anova_table.empty

    # mixed_anova columns: Source, SS, DF1, DF2, MS, F, p-unc, ...
    for col in ["Source", "SS", "DF1", "DF2", "MS", "F", "p-unc"]:
        assert col in anova_table.columns

    # Should have rows for time and group at least
    assert (anova_table["Source"].str.contains("time")).any()
    assert (anova_table["Source"].str.contains("group")).any()
