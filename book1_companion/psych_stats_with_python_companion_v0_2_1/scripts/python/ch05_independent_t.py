#!/usr/bin/env python3
from __future__ import annotations

import pandas as pd
from scipy import stats

from common import ROOT, rounded, write_result


def main() -> None:
    data_file = "data/ch05_independent.csv"
    data = pd.read_csv(ROOT / data_file)
    structured = data.loc[data["group"] == "structured", "test_score"]
    standard = data.loc[data["group"] == "standard", "test_score"]
    test = stats.ttest_ind(structured, standard, equal_var=False)
    v1, v2 = structured.var(ddof=1), standard.var(ddof=1)
    n1, n2 = len(structured), len(standard)
    welch_df = (v1 / n1 + v2 / n2) ** 2 / ((v1 / n1) ** 2 / (n1 - 1) + (v2 / n2) ** 2 / (n2 - 1))
    pooled_sd = (((n1 - 1) * v1 + (n2 - 1) * v2) / (n1 + n2 - 2)) ** 0.5
    fields = {
        "structured_mean": rounded(structured.mean()),
        "structured_sd": rounded(structured.std(ddof=1)),
        "standard_mean": rounded(standard.mean()),
        "standard_sd": rounded(standard.std(ddof=1)),
        "t_statistic": rounded(test.statistic),
        "degrees_of_freedom": rounded(welch_df),
        "p_value": rounded(test.pvalue),
        "cohen_d": rounded((structured.mean() - standard.mean()) / pooled_sd),
    }
    out = write_result("ch05", "Welch independent-samples t-test", data_file, fields)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
