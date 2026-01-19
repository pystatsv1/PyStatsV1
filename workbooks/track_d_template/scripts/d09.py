# SPDX-License-Identifier: MIT
"""Track D convenience wrapper.

Runs: business_ch09_reporting_style_contract.py

Artifacts written to ``--outdir`` (default: ``outputs/track_d``):

* figures/
* ch09_style_contract.json
* ch09_figures_manifest.csv
* ch09_executive_memo.md
* ch09_summary.json


Use either:
  pystatsv1 workbook run d09
or:
  pystatsv1 workbook run business_ch09_reporting_style_contract
"""

from __future__ import annotations

from scripts.business_ch09_reporting_style_contract import main


if __name__ == "__main__":
    main()
