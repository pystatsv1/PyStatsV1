# SPDX-License-Identifier: MIT
"""Track D convenience wrapper.

Runs: business_ch18_expense_forecasting_fixed_variable_step_payroll.py

Artifacts written to ``--outdir`` (default: ``outputs/track_d``):

* figures/
* ch18_expense_monthly_by_account.csv
* ch18_expense_behavior_map.csv
* ch18_payroll_monthly.csv
* ch18_payroll_scenarios_forecast.csv
* ch18_expense_forecast_next12_detail.csv
* ch18_expense_forecast_next12_summary.csv
* ch18_control_plan_template.csv
* ch18_design.json
* ch18_memo.md
* ch18_figures_manifest.csv


Use either:
  pystatsv1 workbook run d18
or:
  pystatsv1 workbook run business_ch18_expense_forecasting_fixed_variable_step_payroll
"""

from __future__ import annotations

from scripts.business_ch18_expense_forecasting_fixed_variable_step_payroll import main


if __name__ == "__main__":
    main()
