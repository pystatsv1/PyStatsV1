# SPDX-License-Identifier: MIT
"""Track D convenience wrapper.

Runs: business_ch20_integrated_forecasting_three_statements.py

Artifacts written to ``--outdir`` (default: ``outputs/track_d``):

* figures/
* ch20_pnl_forecast_monthly.csv
* ch20_balance_sheet_forecast_monthly.csv
* ch20_cash_flow_forecast_monthly.csv
* ch20_assumptions.csv
* ch20_design.json
* ch20_memo.md
* ch20_figures_manifest.csv


Use either:
  pystatsv1 workbook run d20
or:
  pystatsv1 workbook run business_ch20_integrated_forecasting_three_statements
"""

from __future__ import annotations

from scripts.business_ch20_integrated_forecasting_three_statements import main


if __name__ == "__main__":
    main()
