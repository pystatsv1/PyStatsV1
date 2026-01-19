# SPDX-License-Identifier: MIT
"""Track D convenience wrapper.

Runs: business_ch07_preparing_accounting_data_for_analysis.py

Artifacts written to ``--outdir`` (default: ``outputs/track_d``):

* gl_tidy.csv
* gl_monthly_summary.csv
* ch07_summary.json


Use either:
  pystatsv1 workbook run d07
or:
  pystatsv1 workbook run business_ch07_preparing_accounting_data_for_analysis
"""

from __future__ import annotations

from scripts.business_ch07_preparing_accounting_data_for_analysis import main


if __name__ == "__main__":
    main()
