# SPDX-License-Identifier: MIT
"""Track D convenience wrapper.

Runs: business_ch23_communicating_results_governance.py

Artifacts written to ``--outdir`` (default: ``outputs/track_d``):

* ch23_memo_template.md
* ch23_kpi_governance_template.csv
* ch23_dashboard_spec_template.csv
* ch23_red_team_checklist.md
* ch23_design.json


Use either:
  pystatsv1 workbook run d23
or:
  pystatsv1 workbook run business_ch23_communicating_results_governance
"""

from __future__ import annotations

from scripts.business_ch23_communicating_results_governance import main


if __name__ == "__main__":
    main()
