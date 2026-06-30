#!/usr/bin/env python3
from __future__ import annotations

import pandas as pd
from scipy import stats

from common import ROOT, rounded, write_result


def main() -> None:
    data_file = "data/ch11_regression.csv"
    data = pd.read_csv(ROOT / data_file)
    result = stats.linregress(data["study_hours"], data["test_score"])
    fields = {
        "intercept": rounded(result.intercept),
        "slope": rounded(result.slope),
        "slope_standard_error": rounded(result.stderr),
        "t_statistic": rounded(result.slope / result.stderr),
        "degrees_of_freedom": int(len(data) - 2),
        "p_value": rounded(result.pvalue),
        "r_squared": rounded(result.rvalue**2),
        "n": int(len(data)),
    }
    out = write_result("ch11", "Simple linear regression", data_file, fields)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
