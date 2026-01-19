# SPDX-License-Identifier: MIT
"""Track D convenience wrapper.

Runs: business_ch21_scenario_planning_sensitivity_stress.py

Artifacts written to ``--outdir`` (default: ``outputs/track_d``):

* figures/
* ch21_scenario_pack_monthly.csv
* ch21_sensitivity_cash_shortfall.csv
* ch21_assumptions.csv
* ch21_governance_template.csv
* ch21_figures_manifest.csv
* ch21_design.json
* ch21_memo.md


Use either:
  pystatsv1 workbook run d21
or:
  pystatsv1 workbook run business_ch21_scenario_planning_sensitivity_stress
"""

from __future__ import annotations

from scripts.business_ch21_scenario_planning_sensitivity_stress import main


if __name__ == "__main__":
    main()
