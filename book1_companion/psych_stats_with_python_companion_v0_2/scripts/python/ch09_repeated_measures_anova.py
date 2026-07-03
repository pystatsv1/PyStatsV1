#!/usr/bin/env python3
from __future__ import annotations

import pandas as pd
from scipy import stats

from common import ROOT, rounded, write_result


def main() -> None:
    data_file = "data/ch09_repeated_measures.csv"
    data = pd.read_csv(ROOT / data_file)
    wide = data.pivot(index="participant_id", columns="time", values="confidence_score")[
        ["baseline", "week_2", "week_4"]
    ]
    values = wide.to_numpy()
    n, k = values.shape
    grand = values.mean()
    subject_means = values.mean(axis=1)
    time_means = values.mean(axis=0)
    ss_total = ((values - grand) ** 2).sum()
    ss_subjects = k * ((subject_means - grand) ** 2).sum()
    ss_time = n * ((time_means - grand) ** 2).sum()
    ss_error = ss_total - ss_subjects - ss_time
    df_time = k - 1
    df_error = (n - 1) * (k - 1)
    f_value = (ss_time / df_time) / (ss_error / df_error)
    fields = {
        "baseline_mean": rounded(time_means[0]),
        "week_2_mean": rounded(time_means[1]),
        "week_4_mean": rounded(time_means[2]),
        "f_statistic": rounded(f_value),
        "df_time": df_time,
        "df_error": df_error,
        "p_value": rounded(stats.f.sf(f_value, df_time, df_error)),
        "partial_eta_squared": rounded(ss_time / (ss_time + ss_error)),
    }
    out = write_result("ch09", "One-factor repeated-measures ANOVA", data_file, fields)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
