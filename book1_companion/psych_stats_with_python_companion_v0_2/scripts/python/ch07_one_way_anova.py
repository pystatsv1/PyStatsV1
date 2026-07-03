#!/usr/bin/env python3
from __future__ import annotations

import pandas as pd
from scipy import stats

from common import ROOT, rounded, write_result


def main() -> None:
    data_file = "data/ch07_one_way_anova.csv"
    data = pd.read_csv(ROOT / data_file)
    groups = {name: frame["test_score"] for name, frame in data.groupby("study_condition", sort=True)}
    test = stats.f_oneway(*groups.values())
    grand_mean = data["test_score"].mean()
    ss_between = sum(len(values) * (values.mean() - grand_mean) ** 2 for values in groups.values())
    ss_within = sum(((values - values.mean()) ** 2).sum() for values in groups.values())
    fields = {
        "practice_quiz_mean": rounded(groups["practice_quiz"].mean()),
        "retrieval_practice_mean": rounded(groups["retrieval_practice"].mean()),
        "spaced_review_mean": rounded(groups["spaced_review"].mean()),
        "f_statistic": rounded(test.statistic),
        "df_between": 2,
        "df_within": int(len(data) - 3),
        "p_value": rounded(test.pvalue),
        "eta_squared": rounded(ss_between / (ss_between + ss_within)),
    }
    out = write_result("ch07", "One-way ANOVA", data_file, fields)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
