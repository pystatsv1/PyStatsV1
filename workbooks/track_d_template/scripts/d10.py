# SPDX-License-Identifier: MIT
"""Track D convenience wrapper.

Runs: business_ch10_probability_risk.py

Artifacts written to ``--outdir`` (default: ``outputs/track_d``):

* figures/
* ch10_figures_manifest.csv
* ch10_risk_memo.md
* ch10_risk_summary.json


Use either:
  pystatsv1 workbook run d10
or:
  pystatsv1 workbook run business_ch10_probability_risk
"""

from __future__ import annotations

from scripts.business_ch10_probability_risk import main


if __name__ == "__main__":
    main()
