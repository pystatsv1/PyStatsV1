# SPDX-License-Identifier: MIT
"""Track D convenience wrapper.

Runs: business_ch19_cash_flow_forecasting_direct_method_13_week.py

Artifacts written to ``--outdir`` (default: ``outputs/track_d``):

* figures/
* ch19_cash_history_weekly.csv
* ch19_cash_forecast_13w_scenarios.csv
* ch19_cash_assumptions.csv
* ch19_cash_governance_template.csv
* ch19_design.json
* ch19_memo.md
* ch19_figures_manifest.csv


Use either:
  pystatsv1 workbook run d19
or:
  pystatsv1 workbook run business_ch19_cash_flow_forecasting_direct_method_13_week
"""

from __future__ import annotations

from scripts.business_ch19_cash_flow_forecasting_direct_method_13_week import main


if __name__ == "__main__":
    main()
