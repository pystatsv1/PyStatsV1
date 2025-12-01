import pandas as pd
import pytest

from scripts.psych_ch14a_pingouin_rm_demo import (
    simulate_repeated_measures_data,
    run_pingouin_rm_anova,
)


def test_simulate_repeated_measures_data_basic_shape():
    """RM demo should return long-format data with subject, time, stress_score."""
    df = simulate_repeated_measures_data()

    assert isinstance(df, pd.DataFrame)
    for col in ["subject", "time", "stress_score"]:
        assert col in df.columns

    # At least a few participants and 3 time points
    assert df["subject"].nunique() >= 10
    assert set(df["time"].unique()) >= {"pre", "post", "followup"}

    # No missing outcome
    assert df["stress_score"].isna().sum() == 0


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_run_pingouin_rm_anova_returns_table():
    """Pingouin rm_anova wrapper should return a non-empty ANOVA table."""
    df = simulate_repeated_measures_data()
    anova_table = run_pingouin_rm_anova(df)

    assert isinstance(anova_table, pd.DataFrame)
    assert not anova_table.empty

    # Standard rm_anova(detailed=True) columns
    for col in ["Source", "SS", "DF", "MS", "F", "p-unc"]:
        assert col in anova_table.columns

    # At least one finite F and p-unc
    assert pd.api.types.is_numeric_dtype(anova_table["F"])
    assert pd.api.types.is_numeric_dtype(anova_table["p-unc"])
