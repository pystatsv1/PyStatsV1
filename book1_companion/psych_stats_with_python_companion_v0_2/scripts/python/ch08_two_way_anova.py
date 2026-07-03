#!/usr/bin/env python3
from __future__ import annotations

import pandas as pd
import statsmodels.api as sm
from statsmodels.formula.api import ols

from common import ROOT, rounded, write_result


def partial_eta(sum_sq: float, error_sum_sq: float) -> float:
    return sum_sq / (sum_sq + error_sum_sq)


def main() -> None:
    data_file = "data/ch08_two_way_anova.csv"
    data = pd.read_csv(ROOT / data_file)
    model = ols("test_score ~ C(strategy) * C(feedback)", data=data).fit()
    table = sm.stats.anova_lm(model, typ=2)
    error_ss = float(table.loc["Residual", "sum_sq"])
    means = data.groupby(["strategy", "feedback"])["test_score"].mean()
    strategy = table.loc["C(strategy)"]
    feedback = table.loc["C(feedback)"]
    interaction = table.loc["C(strategy):C(feedback)"]
    fields = {
        "standard_no_feedback_mean": rounded(means[("standard", "no_feedback")]),
        "standard_feedback_mean": rounded(means[("standard", "feedback")]),
        "structured_no_feedback_mean": rounded(means[("structured", "no_feedback")]),
        "structured_feedback_mean": rounded(means[("structured", "feedback")]),
        "strategy_f": rounded(strategy["F"]),
        "strategy_p": rounded(strategy["PR(>F)"]),
        "strategy_partial_eta_squared": rounded(partial_eta(strategy["sum_sq"], error_ss)),
        "feedback_f": rounded(feedback["F"]),
        "feedback_p": rounded(feedback["PR(>F)"]),
        "feedback_partial_eta_squared": rounded(partial_eta(feedback["sum_sq"], error_ss)),
        "interaction_f": rounded(interaction["F"]),
        "interaction_p": rounded(interaction["PR(>F)"]),
        "interaction_partial_eta_squared": rounded(partial_eta(interaction["sum_sq"], error_ss)),
        "df_effect": 1,
        "df_error": 44,
    }
    out = write_result("ch08", "Two-way factorial ANOVA", data_file, fields)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
