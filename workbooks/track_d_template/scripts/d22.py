# SPDX-License-Identifier: MIT
"""Track D convenience wrapper.

Runs: business_ch22_financial_statement_analysis_toolkit.py

Artifacts written to ``--outdir`` (default: ``outputs/track_d``):

* figures/
* ch22_ratios_monthly.csv
* ch22_common_size_is.csv
* ch22_common_size_bs.csv
* ch22_variance_bridge_latest.csv
* ch22_assumptions.csv
* ch22_figures_manifest.csv
* ch22_memo.md
* ch22_design.json


Use either:
  pystatsv1 workbook run d22
or:
  pystatsv1 workbook run business_ch22_financial_statement_analysis_toolkit
"""

from __future__ import annotations

from scripts.business_ch22_financial_statement_analysis_toolkit import main


if __name__ == "__main__":
    main()
