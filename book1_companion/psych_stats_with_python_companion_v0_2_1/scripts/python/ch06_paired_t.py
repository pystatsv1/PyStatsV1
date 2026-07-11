#!/usr/bin/env python3
from __future__ import annotations

import pandas as pd
from scipy import stats

from common import ROOT, rounded, write_result


def main() -> None:
    data_file = "data/ch06_paired.csv"
    data = pd.read_csv(ROOT / data_file)
    difference = data["anxiety_post"] - data["anxiety_pre"]
    test = stats.ttest_rel(data["anxiety_post"], data["anxiety_pre"])
    fields = {
        "pre_mean": rounded(data["anxiety_pre"].mean()),
        "post_mean": rounded(data["anxiety_post"].mean()),
        "mean_difference_post_minus_pre": rounded(difference.mean()),
        "t_statistic": rounded(test.statistic),
        "degrees_of_freedom": int(len(data) - 1),
        "p_value": rounded(test.pvalue),
        "cohen_dz": rounded(difference.mean() / difference.std(ddof=1)),
    }
    out = write_result("ch06", "Paired-samples t-test", data_file, fields)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
