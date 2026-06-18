"""Regression tests for Pingouin column-name compatibility helpers."""

from __future__ import annotations

import pandas as pd

from scripts._pingouin_compat import add_pingouin_legacy_aliases


def test_adds_legacy_hyphen_aliases_without_removing_new_columns() -> None:
    table = pd.DataFrame(
        {
            "p_val": [0.01],
            "p_unc": [0.02],
            "p_GG_corr": [0.03],
            "U_val": [12.0],
            "W_val": [8.0],
            "cohen_d": [0.5],
        }
    )

    out = add_pingouin_legacy_aliases(table)

    for source, alias in [
        ("p_val", "p-val"),
        ("p_unc", "p-unc"),
        ("p_GG_corr", "p-GG-corr"),
        ("U_val", "U-val"),
        ("W_val", "W-val"),
        ("cohen_d", "cohen-d"),
    ]:
        assert source in out.columns
        assert alias in out.columns
        assert out.loc[0, alias] == out.loc[0, source]


def test_does_not_overwrite_existing_legacy_columns() -> None:
    table = pd.DataFrame({"p_val": [0.01], "p-val": [0.99]})

    out = add_pingouin_legacy_aliases(table)

    assert out.loc[0, "p-val"] == 0.99
