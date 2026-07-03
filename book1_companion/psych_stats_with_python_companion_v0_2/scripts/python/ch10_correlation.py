#!/usr/bin/env python3
from __future__ import annotations

import pandas as pd
from scipy import stats

from common import ROOT, rounded, write_result


def main() -> None:
    data_file = "data/ch10_correlation.csv"
    data = pd.read_csv(ROOT / data_file)
    test = stats.pearsonr(data["study_hours"], data["test_score"])
    fields = {
        "study_hours_mean": rounded(data["study_hours"].mean()),
        "test_score_mean": rounded(data["test_score"].mean()),
        "correlation_r": rounded(test.statistic),
        "degrees_of_freedom": int(len(data) - 2),
        "p_value": rounded(test.pvalue),
        "n": int(len(data)),
    }
    out = write_result("ch10", "Pearson correlation", data_file, fields)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
